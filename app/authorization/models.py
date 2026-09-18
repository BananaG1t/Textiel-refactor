from django.db import models
from django.contrib.auth.models import Permission

# Create your models here.
class Role(models.Model):
    name = models.CharField(max_length=50, unique=True)
    level = models.PositiveIntegerField()

    permissions = models.ManyToManyField(
        Permission,
        blank=True,
        related_name="roles",
    )

    def __str__(self):
        return self.name