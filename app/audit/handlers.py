import logging


class DatabaseAuditHandler(logging.Handler):
    def emit(self, record):
        try:
            # Import the AuditLog later because the apps arent loaded yet when this file is allocated to the logger (during django setup)
            from .models import AuditLog

            audit = getattr(record, "audit", {})

            AuditLog.objects.create(
                timestamp=record.created,
                level=record.levelname,
                action=audit.get("action", record.getMessage()),
                user_id=audit.get("user_id"),
                object_type=audit.get("object_type"),
                object_id=audit.get("object_id"),
                message=record.getMessage(),
                metadata=audit.get("metadata", {}),
            )
        except Exception:
            self.handleError(record)