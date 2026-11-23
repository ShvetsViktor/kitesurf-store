from django.conf import settings
from django.db import models


class CustomerProfile(models.Model):
    """Store additional information associated with a customer."""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="customer_profile",
    )

    def __str__(self):
        """Return the customer's email address."""
        return self.user.email
