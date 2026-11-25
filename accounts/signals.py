from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

from accounts.models import CustomerProfile


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_customer_profile(sender, instance, created, **kwargs):
    """Create a profile when a new user is created."""
    if created:
        CustomerProfile.objects.create(user=instance)
