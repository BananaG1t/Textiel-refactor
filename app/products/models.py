from django.db import models
from uuid import uuid4

# Create your models here.
class Product(models.Model):
    class ProductType(models.TextChoices):
        CLOTHING = "CLOTHING", "Clothing"
        ACCESSORY = "ACCESSORY", "Accessory"
        BOOK = "BOOK", "Book"
        PRINT = "PRINT", "Print"
        PATCH = "PATCH", "Patch"

    
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    sku = models.CharField(max_length=63, unique=True)
    ean = models.CharField(max_length=13, unique=True, blank=True, null=True)
    name = models.CharField(max_length=255)
    type = models.CharField(choices=ProductType.choices, max_length=20)
    image = models.ImageField(upload_to="products/", blank=True, null=True)
    color = models.CharField(max_length=63, blank=True)
    size = models.CharField(max_length=63, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    weight = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

class Book(models.Model):
    class StatusType(models.TextChoices):
        NEW = "NEW", "New"
        USED = "USED", "Used"

    product = models.OneToOneField(
        Product,
        on_delete=models.CASCADE,
        related_name="book",
    )
    isbn = models.CharField(max_length=13, unique=True)
    authors = models.JSONField(default=list)
    status = models.CharField(
        max_length=20,
        choices=StatusType.choices,
        blank=True,
    )

class PrintPatch(models.Model):
    product = models.OneToOneField(Product, on_delete=models.CASCADE, related_name="print_patch")
    dimensions = models.JSONField(default=dict, blank=True) # {width: int, height: int}

class PrintPatchFile(models.Model):
    print_patch = models.ForeignKey(PrintPatch, on_delete=models.CASCADE, related_name="files")
    file = models.FileField(upload_to="print_patches/")
    file_type = models.CharField(max_length=63) # e.g., "SVG", "PNG", "PDF"