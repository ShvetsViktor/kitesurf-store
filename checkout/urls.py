from django.urls import path
from .webhooks import stripe_webhook

from . import views


urlpatterns = [
    path("", views.checkout, name="checkout"),
    path("success/", views.checkout_success, name="checkout_success"),
    path("cancel/", views.checkout_cancel, name="checkout_cancel"),
    path("webhook/", stripe_webhook, name="stripe_webhook"),
]
