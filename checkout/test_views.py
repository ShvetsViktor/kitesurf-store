from decimal import Decimal

from django.test import TestCase
from django.urls import reverse

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
