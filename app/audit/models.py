from django.db import models

# Create your models here.
class AuditLog(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)

    level = models.CharField(max_length=20)
    action = models.CharField(max_length=100)

    user = models.ForeignKey("users.User", on_delete=models.PROTECT, null=True, blank=True)

    object_type = models.CharField(max_length=100, null=True, blank=True)
    object_id = models.CharField(max_length=100, null=True, blank=True)

    message = models.TextField()

    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["-timestamp"]
        indexes = [
            models.Index(fields=["timestamp"]),
            models.Index(fields=["action"]),
            models.Index(fields=["user_id"]),
            models.Index(fields=["object_type", "object_id"]),
        ]