from uuid import UUID

from django.db import models, transaction

from app.orders.models import Order
from app.users.models import User
from products.models import Product

# Create your models here.
class InventoryManager(models.Manager):
    def _lock_order(self, order: Order) -> tuple[Order, list, dict[UUID, Inventory]]:
        order = Order.objects.select_for_update().get(pk=order.pk)
        items = list(order.items.select_related("product").select_for_update().all())
        inventories = {
            inventory.product_id: inventory
            for inventory in Inventory.objects.select_for_update().filter(
                product_id__in=[item.product_id for item in items]
            )
        }
        return order, items, inventories

    def can_allocate_order(self, items, inventories: dict[UUID, Inventory]) -> bool:
        for item in items:
            inventory = inventories[item.product_id]
            if inventory.available_quantity < item.quantity:
                return False
        return True

    @transaction.atomic
    def try_allocate_order(self, order: Order):
        order, items, inventories = self._lock_order(order)

        if StockAllocation.objects.filter(order=order).exists():
            return False
        
        if not self.can_allocate_order(items, inventories):
            return False
        for item in items:
            StockAllocation.objects.create(
                order=order,
                inventory=inventories[item.product_id],
                quantity=item.quantity 
            )
            inventories[item.product_id].reserved_quantity += item.quantity
            inventories[item.product_id].save(update_fields=["reserved_quantity"])
        return True

    @transaction.atomic
    def release_order(self, order: Order):
        order, _, inventories = self._lock_order(order)

        allocations = list(
            StockAllocation.objects
            .select_for_update()
            .filter(order=order)
            .select_related("inventory")
        )

        for allocation in allocations:
            inventory = inventories[allocation.inventory.product_id]
            inventory.reserved_quantity -= allocation.quantity
            inventory.save(update_fields=["reserved_quantity"])
            allocation.delete()

    @transaction.atomic
    def reconcile_order(self, order: Order):
        order, items, inventories = self._lock_order(order)

        allocations = list(
            StockAllocation.objects
            .select_for_update()
            .filter(order=order)
            .select_related("inventory")
        )

        items_by_product = {
            item.product_id: item
            for item in items
        }

        allocations_by_product = {
            allocation.inventory.product_id: allocation
            for allocation in allocations
        }

        

        # Remove allocations for products no longer in the order
        for product_id, allocation in allocations_by_product.items():
            if product_id not in items_by_product:
                inventory = inventories[product_id]
                inventory.reserved_quantity -= allocation.quantity
                inventory.save(update_fields=["reserved_quantity"])
                allocation.delete()

        # Create or adjust allocations
        for product_id, item in items_by_product.items():
            inventory = inventories[product_id]
            allocation = allocations_by_product.get(product_id)

            if allocation is None:
                if inventory.available_quantity < item.quantity:
                    raise ValueError(
                        f"Not enough available inventory for product "
                        f"{item.product.name} to reconcile order {order.id}"
                    )

                StockAllocation.objects.create(
                    order=order,
                    inventory=inventory,
                    quantity=item.quantity,
                )

                inventory.reserved_quantity += item.quantity
                inventory.save(update_fields=["reserved_quantity"])

            else:
                difference = item.quantity - allocation.quantity

                if difference > 0:
                    if inventory.available_quantity < difference:
                        raise ValueError(
                            f"Not enough available inventory for product "
                            f"{item.product.name} to reconcile order {order.id}"
                        )

                inventory.reserved_quantity += difference
                inventory.save(update_fields=["reserved_quantity"])

                allocation.quantity = item.quantity
                allocation.save(update_fields=["quantity"])
                    
    
class Inventory(models.Model):
    product = models.OneToOneField(
        Product,
        on_delete=models.CASCADE,
        related_name="inventory",
    )
    quantity = models.PositiveIntegerField(default=0)
    reserved_quantity = models.PositiveIntegerField(default=0)
    backorder_quantity = models.PositiveIntegerField(default=0)

    objects = InventoryManager()

    @property
    def available_quantity(self):
        return self.quantity - self.reserved_quantity

class StockMovement(models.Model):
    class MovementType(models.TextChoices):
        CREATED = "CREATED", 'Created'
        RECEIVED = "RECEIVED", "Received"
        PRINTED = "PRINTED", "Printed"
        SOLD = "SOLD", "Sold"
        RETURNED = "RETURNED", "Returned"
        DAMAGED = "DAMAGED", "Damaged"
        ADJUSTMENT = "ADJUSTMENT", "Adjustment"

    inventory = models.ForeignKey(
        Inventory,
        on_delete=models.CASCADE,
        related_name="stock_movements",
    )
    amount = models.IntegerField()

    @property
    def singed_amount(self):
        return f"{self.amount:+}"
    
    quantity_after = models.PositiveIntegerField()
    movement_type = models.CharField(
        max_length=20,
        choices=MovementType.choices,
    )
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.product} {self.amount:+}"

class StockAllocation(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="allocations")
    inventory = models.ForeignKey(Inventory, on_delete=models.PROTECT, related_name="allocations")
    quantity = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["order", "inventory"], name="unique_allocation_per_order_inventory")
        ]