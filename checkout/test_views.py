from decimal import Decimal

from django.test import TestCase
from django.urls import reverse
from unittest.mock import patch

from checkout.models import Order, OrderItem
from products.models import Category, Product


class CheckoutViewTests(TestCase):
    """Test checkout page and shopping bag validation."""

    @classmethod
    def setUpTestData(cls):
        cls.category = Category.objects.create(
            name="Kites",
            slug="checkout-kites",
        )
        cls.product = Product.objects.create(
            category=cls.category,
            sku="CHECKOUT-VIEW-001",
            name="Test Kite",
            description="Test product",
            price=Decimal("150.00"),
            stock=5,
            is_active=True,
        )

    def setUp(self):
        self.url = reverse("checkout")

    def set_bag(self, quantity):
        """Add a product to the session shopping bag."""
        session = self.client.session
        session["bag"] = {str(self.product.pk): quantity}
        session.save()

    def test_checkout_page_displays_form_and_total(self):
        """Display checkout form and server-calculated total."""
        self.set_bag(2)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response,
            "checkout/checkout.html",
        )
        self.assertIn("form", response.context)
        self.assertEqual(
            response.context["total"],
            Decimal("300.00"),
        )

    def test_empty_bag_redirects_to_bag(self):
        """Prevent checkout with an empty shopping bag."""
        response = self.client.get(self.url)

        self.assertRedirects(
            response,
            reverse("bag_detail"),
        )

    def test_unavailable_product_redirects_to_bag(self):
        """Reject checkout when a product becomes unavailable."""
        self.set_bag(1)

        self.product.is_active = False
        self.product.save()

        response = self.client.get(self.url)

        self.assertRedirects(
            response,
            reverse("bag_detail"),
        )

    def test_insufficient_stock_redirects_to_bag(self):
        """Reject checkout when quantity exceeds stock."""
        self.set_bag(6)

        response = self.client.get(self.url)

        self.assertRedirects(
            response,
            reverse("bag_detail"),
        )

    def test_checkout_uses_current_database_price(self):
        """Use current product prices rather than session values."""
        self.set_bag(2)

        self.product.price = Decimal("200.00")
        self.product.save()

        response = self.client.get(self.url)

        self.assertEqual(
            response.context["total"],
            Decimal("400.00"),
        )

    @patch("checkout.views.stripe.checkout.Session.create")
    def test_valid_checkout_creates_pending_order(self, mock_create):
        """Create a pending order from valid checkout details."""
        mock_create.return_value.id = "cs_test_pending_order"
        mock_create.return_value.url = (
            "https://checkout.stripe.com/test-session"
        )
        self.set_bag(2)

        response = self.client.post(
            self.url,
            {
                "full_name": "John Smith",
                "email": "john@example.com",
                "phone_number": "07123456789",
                "address_line_1": "10 High Street",
                "address_line_2": "",
                "city": "Manchester",
                "county": "Greater Manchester",
                "postcode": "M1 1AA",
            },
        )

        self.assertEqual(Order.objects.count(), 1)

        order = Order.objects.get()

        self.assertEqual(order.status, Order.Status.PENDING)
        self.assertEqual(order.order_total, Decimal("300.00"))
        self.assertEqual(order.grand_total, Decimal("300.00"))
        self.assertEqual(order.delivery_cost, Decimal("0.00"))
        self.assertEqual(order.email, "john@example.com")

        self.assertEqual(OrderItem.objects.count(), 1)

        order_item = OrderItem.objects.get()

        self.assertEqual(order_item.order, order)
        self.assertEqual(order_item.product, self.product)
        self.assertEqual(order_item.quantity, 2)
        self.assertEqual(order_item.price, Decimal("150.00"))

        self.assertEqual(response.status_code, 302)

    def test_invalid_checkout_does_not_create_order(self):
        """Reject invalid delivery details without creating an order."""
        self.set_bag(1)

        response = self.client.post(
            self.url,
            {
                "full_name": "",
                "email": "invalid-email",
                "phone_number": "",
                "address_line_1": "",
                "city": "",
                "postcode": "INVALID",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Order.objects.count(), 0)
        self.assertEqual(OrderItem.objects.count(), 0)
        self.assertTrue(response.context["form"].errors)

    def test_checkout_revalidates_stock_on_post(self):
        """Prevent creating an order when stock is insufficient."""
        self.set_bag(6)

        response = self.client.post(
            self.url,
            {
                "full_name": "John Smith",
                "email": "john@example.com",
                "phone_number": "07123456789",
                "address_line_1": "10 High Street",
                "city": "Manchester",
                "county": "Greater Manchester",
                "postcode": "M1 1AA",
            },
        )

        self.assertRedirects(response, reverse("bag_detail"))
        self.assertEqual(Order.objects.count(), 0)

    @patch("checkout.views.stripe.checkout.Session.create")
    def test_valid_checkout_creates_stripe_session(self, mock_create):
        """Create Stripe Checkout Session for a valid order."""
        self.set_bag(2)

        mock_create.return_value.id = "cs_test_123"
        mock_create.return_value.url = (
            "https://checkout.stripe.com/test-session"
        )

        response = self.client.post(
            self.url,
            {
                "full_name": "John Smith",
                "email": "john@example.com",
                "phone_number": "07123456789",
                "address_line_1": "10 High Street",
                "address_line_2": "",
                "city": "Manchester",
                "county": "Greater Manchester",
                "postcode": "M1 1AA",
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response.url,
            "https://checkout.stripe.com/test-session",
        )

        order = Order.objects.get()

        self.assertEqual(
            order.stripe_session_id,
            "cs_test_123",
        )
        self.assertEqual(
            order.status,
            Order.Status.PENDING,
        )

        mock_create.assert_called_once()
