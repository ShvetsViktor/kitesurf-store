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


class DeliveryAddress(models.Model):
    """Store a customer's delivery address."""

    profile = models.ForeignKey(
        CustomerProfile,
        on_delete=models.CASCADE,
        related_name="delivery_addresses",
    )
    full_name = models.CharField(max_length=150)
    address_line_1 = models.CharField(max_length=255)
    address_line_2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100)
    county = models.CharField(max_length=100, blank=True)
    postcode = models.CharField(max_length=8)
    phone_number = models.CharField(max_length=20, blank=True)
    is_default = models.BooleanField(default=False)

    def __str__(self):
        """Return a readable address description."""
        return f"{self.full_name} - {self.postcode}"
