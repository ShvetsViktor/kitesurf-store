from decimal import Decimal

from django.test import TestCase
from django.urls import reverse

from products.models import Category, Product
from .utils import get_bag_details


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

    def test_adding_same_product_increases_quantity(self):
        """Verify adding the same product twice increases its quantity."""
        self.client.post(
            reverse(
                "bag_add",
                args=[self.active_product.pk],
            )
        )

        self.client.post(
            reverse(
                "bag_add",
                args=[self.active_product.pk],
            )
        )

        session = self.client.session
        bag = session.get("bag")

        self.assertEqual(bag[str(self.active_product.pk)], 2)

    def test_cannot_add_nonexistent_product(self):
        """Verify nonexistent products cannot be added to the bag."""
        response = self.client.post(
            reverse(
                "bag_add",
                args=[999999],
            )
        )

        bag = self.client.session.get("bag", {})

        self.assertEqual(response.status_code, 404)
        self.assertNotIn("999999", bag)

    def test_update_product_quantity(self):
        """Verify an existing bag item's quantity can be updated."""
        self.client.post(
            reverse("bag_add", args=[self.active_product.pk])
        )
        self.client.post(
            reverse("bag_update", args=[self.active_product.pk]),
            {"quantity": 3}
        )
        bag = self.client.session.get("bag", {})

        self.assertEqual(
            bag[str(self.active_product.pk)],
            3
        )

    def test_removing_product_preserves_other_bag_items(self):
        """Verify removing one product does not affect other bag items."""
        active_product_second = Product.objects.create(
            category=self.category,
            sku="KITE-004",
            name="Hectic Kite",
            description="Test description",
            price=Decimal("500.00"),
            stock=5,
            is_active=True,
        )

        self.client.post(
            reverse("bag_add", args=[self.active_product.pk])
        )
        self.client.post(
            reverse("bag_add", args=[active_product_second.pk])
        )
        self.client.post(
            reverse("bag_remove", args=[self.active_product.pk])
        )
        bag = self.client.session.get("bag", {})

        self.assertIn(str(active_product_second.pk), bag)
        self.assertNotIn(str(self.active_product.pk), bag)
        self.assertEqual(bag[str(active_product_second.pk)], 1)

    def test_bag_calculates_item_subtotal(self):
        """Verify item subtotal equals product price multiplied by quantity."""
        self.client.post(
            reverse("bag_add", args=[self.active_product.pk])
        )
        self.client.post(
            reverse("bag_add", args=[self.active_product.pk])
        )
        bag = self.client.session.get("bag", {})
        details = get_bag_details(bag)
        item = details["items"][0]

        self.assertEqual(
            item["subtotal"],
            self.active_product.price * 2,
        )
