from decimal import Decimal
from unittest.mock import patch
import stripe

from django.test import TestCase
from django.urls import reverse

from checkout.models import Order


class StripeWebhookTests(TestCase):
    """Test Stripe webhook payment confirmation."""

    @patch("checkout.webhooks.stripe.Webhook.construct_event")
    def test_paid_checkout_session_marks_order_paid(self, mock_event):
        """Mark a pending order as paid after verified Stripe payment."""
        order = Order.objects.create(
            full_name="John Smith",
            email="john@example.com",
            address_line_1="10 High Street",
            city="Manchester",
            postcode="M1 1AA",
            order_total=Decimal("150.00"),
            delivery_cost=Decimal("0.00"),
            grand_total=Decimal("150.00"),
            status=Order.Status.PENDING,
            stripe_session_id="cs_test_123",
        )

        mock_event.return_value = {
            "type": "checkout.session.completed",
            "data": {
                "object": {
                    "id": "cs_test_123",
                    "payment_status": "paid",
                    "amount_total": 15000,
                    "currency": "gbp",
                }
            },
        }

        response = self.client.post(
            reverse("stripe_webhook"),
            data=b'{"test": true}',
            content_type="application/json",
            HTTP_STRIPE_SIGNATURE="test_signature",
        )

        self.assertEqual(response.status_code, 200)

        order.refresh_from_db()

        self.assertEqual(order.status, Order.Status.PAID)

    @patch("checkout.webhooks.stripe.Webhook.construct_event")
    def test_invalid_signature_rejected(self, mock_event):
        """Reject webhook requests with invalid Stripe signatures."""
        mock_event.side_effect = stripe.error.SignatureVerificationError(
            "Invalid signature",
            "test_signature",
        )

        response = self.client.post(
            reverse("stripe_webhook"),
            data=b'{"test": true}',
            content_type="application/json",
            HTTP_STRIPE_SIGNATURE="invalid_signature",
        )

        self.assertEqual(response.status_code, 400)

    @patch("checkout.webhooks.stripe.Webhook.construct_event")
    def test_incorrect_payment_amount_rejected(self, mock_event):
        """Reject payment confirmation when Stripe amount differs."""
        order = Order.objects.create(
            full_name="John Smith",
            email="john@example.com",
            address_line_1="10 High Street",
            city="Manchester",
            postcode="M1 1AA",
            order_total=Decimal("150.00"),
            delivery_cost=Decimal("0.00"),
            grand_total=Decimal("150.00"),
            stripe_session_id="cs_test_wrong_amount",
        )

        mock_event.return_value = {
            "type": "checkout.session.completed",
            "data": {
                "object": {
                    "id": "cs_test_wrong_amount",
                    "payment_status": "paid",
                    "amount_total": 10000,
                    "currency": "gbp",
                }
            },
        }

        response = self.client.post(
            reverse("stripe_webhook"),
            data=b'{"test": true}',
            content_type="application/json",
            HTTP_STRIPE_SIGNATURE="test_signature",
        )

        order.refresh_from_db()

        self.assertEqual(response.status_code, 400)
        self.assertEqual(order.status, Order.Status.PENDING)

    @patch("checkout.webhooks.stripe.Webhook.construct_event")
    def test_duplicate_webhook_does_not_reprocess_order(self, mock_event):
        """Keep an already paid order unchanged on duplicate events."""
        order = Order.objects.create(
            full_name="John Smith",
            email="john@example.com",
            address_line_1="10 High Street",
            city="Manchester",
            postcode="M1 1AA",
            order_total=Decimal("150.00"),
            delivery_cost=Decimal("0.00"),
            grand_total=Decimal("150.00"),
            status=Order.Status.PAID,
            stripe_session_id="cs_test_duplicate",
        )

        mock_event.return_value = {
            "type": "checkout.session.completed",
            "data": {
                "object": {
                    "id": "cs_test_duplicate",
                    "payment_status": "paid",
                    "amount_total": 15000,
                    "currency": "gbp",
                }
            },
        }

        response = self.client.post(
            reverse("stripe_webhook"),
            data=b'{"test": true}',
            content_type="application/json",
            HTTP_STRIPE_SIGNATURE="test_signature",
        )

        order.refresh_from_db()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(order.status, Order.Status.PAID)

    @patch("checkout.webhooks.stripe.Webhook.construct_event")
    def test_webhook_handles_real_stripe_session_object(self, mock_event):
        """Handle Stripe Session objects returned by the Stripe SDK."""
        order = Order.objects.create(
            full_name="John Smith",
            email="john@example.com",
            address_line_1="10 High Street",
            city="Manchester",
            postcode="M1 1AA",
            order_total=Decimal("150.00"),
            delivery_cost=Decimal("0.00"),
            grand_total=Decimal("150.00"),
            status=Order.Status.PENDING,
            stripe_session_id="cs_test_stripe_object",
        )

        mock_event.return_value = {
            "type": "checkout.session.completed",
            "data": {
                "object": stripe.checkout.Session.construct_from(
                    {
                        "id": "cs_test_stripe_object",
                        "payment_status": "paid",
                        "amount_total": 15000,
                        "currency": "gbp",
                    },
                    "sk_test_dummy",
                )
            },
        }

        response = self.client.post(
            reverse("stripe_webhook"),
            data=b'{"test": true}',
            content_type="application/json",
            HTTP_STRIPE_SIGNATURE="test_signature",
        )

        order.refresh_from_db()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(order.status, Order.Status.PAID)
