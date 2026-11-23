from django.apps import AppConfig


class AccountsConfig(AppConfig):
    """Configure the accounts application."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "accounts"

    def ready(self):
        """Register account signals."""
        from . import signals  # noqa: F401
