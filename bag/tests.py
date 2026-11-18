from decimal import Decimal

from django.test import TestCase
from django.urls import reverse

from products.models import Category, Product


class ShoppingBagTests(TestCase):
    """Test session-based shopping bag functionality."""
    def setUp(self):
        self.category = Category.objects.create(
            name="Kites",
            slug="kites",
        )

        self.active_product = Product.objects.create(
            category=self.category,
            sku="KITE-001",
            name="Active Kite",
            description="Test description",
            price=Decimal("500.00"),
            stock=5,
            is_active=True,
        )

        self.inactive_product = Product.objects.create(
            category=self.category,
            sku="KITE-002",
            name="Inactive Kite",
            description="Test description",
            price=Decimal("600.00"),
            stock=5,
            is_active=False,
        )

        self.out_of_stock_product = Product.objects.create(
            category=self.category,
            sku="KITE-003",
            name="Out of Stock Kite",
            description="Test description",
            price=Decimal("700.00"),
            stock=0,
            is_active=True,
        )

    def test_add_available_product_to_empty_bag(self):
        """Verify adding an available product to an empty session bag."""
        response = self.client.post(
            reverse(
                "bag_add",
                args=[self.active_product.pk],
            )
        )

        session = self.client.session
        bag = session.get("bag")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(bag, {str(self.active_product.pk): 1})
