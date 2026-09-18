from django.db import models
from products.models import Product

# Create your models here.
class Order(models.Model):
    class OrderStatus(models.TextChoices):
        PENDING = "PENDING", "Pending"
        RESERVED = "RESERVED", "Reserved"
        PROCESSING = "PROCESSING", "Processing"
        COMPLETED = "COMPLETED", "Completed"
        CANCELLED = "CANCELLED", "Cancelled"
        RETURNED = "RETURNED", "Returned"

    status = models.CharField(
        max_length=20,
        choices=OrderStatus.choices,
        default=OrderStatus.PENDING,
    )
    created_at = models.DateField(auto_now_add=True)

    '''crate = models.OneToOneField(
        'crates.Crate',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='order'
    )'''

    def __str__(self):
        return f"order {self.id}, status: {self.status}"

class OrderItem(models.Model):
    order: Order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product: Product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name="order_items")
    quantity = models.PositiveIntegerField()

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["order", "product"], name="unique_order_product"),
        ]

    def __str__(self):
        return f"{self.product.name} quantity: {self.quantity}"