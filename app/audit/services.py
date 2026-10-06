import logging


class AuditLogger:
    def __init__(self):
        self._logger = logging.getLogger("audit")

    def _log(
        self,
        level,
        message,
        *,
        action,
        user_id=None,
        object_type=None,
        object_id=None,
        metadata=None,
    ):
        self._logger.log(
            level,
            message,
            extra={
                "audit": {
                    "action": action,
                    "user_id": user_id,
                    "object_type": object_type,
                    "object_id": object_id,
                    "metadata": metadata or {},
                }
            },
        )

    def debug(self, message, **kwargs):
        self._log(logging.DEBUG, message, **kwargs)

    def info(self, message, **kwargs):
        self._log(logging.INFO, message, **kwargs)

    def warning(self, message, **kwargs):
        self._log(logging.WARNING, message, **kwargs)

    def error(self, message, **kwargs):
        self._log(logging.ERROR, message, **kwargs)

def get_form_changes(form, fields=None):
    changes = {}

    for field in form.changed_data:
        if fields is not None and field not in fields:
            continue

        changes[field] = {
            "old": str(form.initial.get(field)),
            "new": str(form.cleaned_data.get(field)),
        }

    return changes

audit_logger = AuditLogger()