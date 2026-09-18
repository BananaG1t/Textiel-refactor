from django.db import models
from orders.models import Order

# Create your models here.
class Crate(models.Model):
    class CrateStatus(models.TextChoices):
        IDLE = "IDLE", "idle"
        PICKING = "PICKING", "Picking"
        PRINTING = "PRINTING", "Printing"
        PROCESSING = "PROCESSING", "Processing"


    id = models.PositiveIntegerField(primary_key=True, unique=True)
    code = models.PositiveIntegerField(unique=True)
    status = models.CharField(max_length=20, choices=CrateStatus.choices, default=CrateStatus.IDLE)

    @property
    def has_order(self):
        try:
            self.order
            return True
        except Order.DoesNotExist:
            return False

    def __str__(self):
        return f"Crate nr: {self.id}"