from django.db import transaction
from inventory.models import StockMovement
from inventory.services import lock_products
from .models import Order, OrderItemAllocation


def _order_product_ids(order: Order) -> tuple[list, set]:
    """Fetch order items and every product id they touch (variant + base)."""
    order_items = list(order.items.select_related("product").all())
    product_ids = set()
    for item in order_items:
        product_ids.add(item.product_id)
        if item.product.base_product_id:
            product_ids.add(item.product.base_product_id)
    return order_items, product_ids


def _allocation_totals(order: Order):
    return dict(
        OrderItemAllocation.objects.filter(order=order).values_list("product_id", "quantity")
    )


@transaction.atomic
def reserve_order(order: Order) -> bool:
    if order.status != Order.OrderStatus.PENDING:
        raise ValueError("Only pending orders can be reserved.")

    order_items, product_ids = _order_product_ids(order)
    products = lock_products(product_ids)
    for item in order_items:
        item.product = products[item.product_id]

    allocation_totals = {}  # product_id -> quantity, merged as we go

    for item in order_items:
        product = item.product
        base = products.get(product.base_product_id)
        own_available = product.available

        if item.quantity <= own_available:
            product.reserved_quantity += item.quantity
            allocation_totals[product.id] = allocation_totals.get(product.id, 0) + item.quantity
            continue

        if base is None:
            return False

        needed_from_base = item.quantity - max(own_available, 0)
        if needed_from_base > base.available:
            return False

        if own_available > 0:
            product.reserved_quantity += own_available
            allocation_totals[product.id] = allocation_totals.get(product.id, 0) + own_available
        base.reserved_quantity += needed_from_base
        allocation_totals[base.id] = allocation_totals.get(base.id, 0) + needed_from_base

    for product in products.values():
        product.save(update_fields=["reserved_quantity"])

    OrderItemAllocation.objects.bulk_create([
        OrderItemAllocation(order=order, product_id=pid, quantity=qty)
        for pid, qty in allocation_totals.items()
    ])

    order.status = Order.OrderStatus.RESERVED
    order.save(update_fields=["status"])
    return True


@transaction.atomic
def _unreserve_reservations(order: Order) -> bool:
    totals = _allocation_totals(order)
    if not totals:
        return True

    products = lock_products(totals.keys())
    for product_id, qty in totals.items():
        products[product_id].reserved_quantity -= qty

    for product in products.values():
        product.save(update_fields=["reserved_quantity"])

    OrderItemAllocation.objects.filter(order=order).delete()
    return True


@transaction.atomic
def unreserve_order(order: Order) -> bool:
    if order.status not in (Order.OrderStatus.RESERVED, Order.OrderStatus.PROCESSING):
        raise ValueError("Only reserved or processing orders can be unreserved.")

    if not _unreserve_reservations(order):
        return False

    order.status = Order.OrderStatus.PENDING
    order.save(update_fields=["status"])
    return True


@transaction.atomic
def complete_order(order: Order):
    if order.status not in (Order.OrderStatus.RESERVED, Order.OrderStatus.PROCESSING):
        raise ValueError("Only reserved or processing orders can be completed.")

    totals = _allocation_totals(order)
    if not totals:
        raise ValueError(f"{order} has no allocations to complete.")

    products = lock_products(totals.keys())
    for product_id, needed in totals.items():
        product = products[product_id]

        if needed > product.reserved_quantity:
            raise ValueError(
                f"{product} does not have enough reserved stock "
                f"to complete this order."
            )

        if needed > product.quantity:
            raise ValueError(
                f"{product} does not have enough stock "
                f"to complete this order."
            )

        product.quantity -= needed
        product.reserved_quantity -= needed

        product.save(
            update_fields=["quantity", "reserved_quantity"]
        )

        StockMovement.objects.create(
            product=product,
            amount=-needed,
            quantity_after=product.quantity,
            movement_type=StockMovement.MovementType.SOLD,
            user=None,
        )

    OrderItemAllocation.objects.filter(order=order).delete()

    order.status = Order.OrderStatus.COMPLETED
    order.save(update_fields=["status"])


_CANCELLABLE_STATUSES = (
    Order.OrderStatus.PENDING,
    Order.OrderStatus.RESERVED,
    Order.OrderStatus.PROCESSING,
)


@transaction.atomic
def cancel_order(order: Order):
    if order.status not in _CANCELLABLE_STATUSES:
        raise ValueError(f"Cannot cancel an order with status {order.status}.")

    if order.status in (Order.OrderStatus.RESERVED, Order.OrderStatus.PROCESSING):
        if not _unreserve_reservations(order):
            raise ValueError(f"Could not release reservations for {order} while cancelling.")

    order.status = Order.OrderStatus.CANCELLED
    order.save(update_fields=["status"])

def get_print_list(order: Order):
    """Returns [(base_product, derived_product, quantity_to_convert), ...]
    for every derived line item whose own stock allocation didn't fully
    cover its quantity."""
    allocation_totals = _allocation_totals(order)  # {product_id: quantity}
    print_list = []

    for item in order.items.select_related("product", "product__base_product").all():
        product = item.product
        if not product.is_derived:
            continue

        allocated_own = allocation_totals.get(product.id, 0)
        needed = item.quantity - allocated_own
        if needed > 0:
            print_list.append((product.base_product, product, needed))

    return print_list

@transaction.atomic
def complete_printing(order: Order):
    if order.status != Order.OrderStatus.PROCESSING:
        raise ValueError("Only processing orders can complete printing.")

    print_list = get_print_list(order)

    if not print_list:
        raise ValueError(f"{order} has nothing to print.")

    product_ids = {
        product.id
        for base_product, product, quantity in print_list
        for product in (base_product, product)
    }

    products = lock_products(product_ids)

    for base_product, derived_product, quantity in print_list:
        base = products[base_product.id]
        derived = products[derived_product.id]

        allocation = (
            OrderItemAllocation.objects
            .select_for_update()
            .get(
                order=order,
                product=base,
            )
        )

        if allocation.quantity < quantity:
            raise ValueError(
                f"{order} has only {allocation.quantity} allocated "
                f"{base}, but needs {quantity}."
            )

        if base.reserved_quantity < quantity:
            raise ValueError(
                f"{base} has only {base.reserved_quantity} reserved, "
                f"but needs {quantity}."
            )

        # Consume the base product that was used for printing.
        base.quantity -= quantity
        base.reserved_quantity -= quantity

        # The printed product now exists and is reserved for this order.
        derived.quantity += quantity
        derived.reserved_quantity += quantity

        # Move the allocation from base -> derived.
        allocation.quantity -= quantity

        if allocation.quantity == 0:
            allocation.delete()
        else:
            allocation.save(update_fields=["quantity"])

        derived_allocation, created = (
            OrderItemAllocation.objects
            .select_for_update()
            .get_or_create(
                order=order,
                product=derived,
                defaults={"quantity": quantity},
            )
        )

        if not created:
            derived_allocation.quantity += quantity
            derived_allocation.save(update_fields=["quantity"])

        base.save(update_fields=["quantity", "reserved_quantity"])
        derived.save(update_fields=["quantity", "reserved_quantity"])

        # Physical stock movements.
        StockMovement.objects.create(
            product=base,
            amount=-quantity,
            quantity_after=base.quantity,
            movement_type=StockMovement.MovementType.PRINTED,
            user=None,
        )

        StockMovement.objects.create(
            product=derived,
            amount=quantity,
            quantity_after=derived.quantity,
            movement_type=StockMovement.MovementType.PRINTED,
            user=None,
        )