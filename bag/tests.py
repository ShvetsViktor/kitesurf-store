from decimal import Decimal

from django.test import TestCase
from django.urls import reverse

from products.models import Category, Product, ProductImage
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

    def test_bag_calculates_grand_total(self):
        """Verify bag total equals the sum of all item subtotals."""
        active_product_second = Product.objects.create(
            category=self.category,
            sku="KITE-005",
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
            reverse("bag_add", args=[self.active_product.pk])
        )
        self.client.post(
            reverse("bag_add", args=[active_product_second.pk])
        )
        bag = self.client.session.get("bag", {})
        details = get_bag_details(bag)
        total = details["total"]
        expected_total = (self.active_product.price * 2
                          + active_product_second.price)

        self.assertEqual(
            total,
            expected_total
        )

    def test_cannot_add_inactive_product_to_bag(self):
        """Verify inactive products cannot be added to the shopping bag."""
        response = self.client.post(
            reverse("bag_add", args=[self.inactive_product.pk])
        )
        bag = self.client.session.get("bag", {})

        self.assertNotIn(str(self.inactive_product.pk), bag)
        self.assertEqual(response.status_code, 404)

    def test_cannot_add_out_of_stock_product_to_bag(self):
        """Verify out-of-stock products cannot be added to the bag."""
        response = self.client.post(
            reverse("bag_add", args=[self.out_of_stock_product.pk])
        )
        bag = self.client.session.get("bag", {})

        self.assertNotIn(str(self.out_of_stock_product.pk), bag)
        self.assertEqual(response.status_code, 404)

    def test_cannot_add_more_than_available_stock(self):
        """Verify bag quantity cannot exceed available product stock."""
        self.client.post(
            reverse("bag_add", args=[self.active_product.pk])
        )
        self.client.post(
            reverse("bag_add", args=[self.active_product.pk])
        )
        self.client.post(
            reverse("bag_add", args=[self.active_product.pk])
        )
        self.client.post(
            reverse("bag_add", args=[self.active_product.pk])
        )
        self.client.post(
            reverse("bag_add", args=[self.active_product.pk])
        )
        self.client.post(
            reverse("bag_add", args=[self.active_product.pk])
        )
        bag = self.client.session.get("bag", {})

        self.assertEqual(
            bag[str(self.active_product.pk)],
            self.active_product.stock
        )

    def test_cannot_update_nonexistent_product(self):
        """Verify nonexistent products cannot be updated in the bag."""
        response = self.client.post(
            reverse("bag_update", args=[999999]),
            {"quantity": 1}
        )
        bag = self.client.session.get("bag", {})

        self.assertNotIn("999999", bag)
        self.assertEqual(response.status_code, 404)

    def test_cannot_update_inactive_product(self):
        """Verify inactive products cannot be updated in the bag."""
        response = self.client.post(
            reverse("bag_update", args=[self.inactive_product.pk]),
            {"quantity": 3}
        )
        bag = self.client.session.get("bag", {})

        self.assertEqual(response.status_code, 404)
        self.assertNotIn(str(self.inactive_product.pk), bag)

    def test_cannot_update_out_of_stock_product(self):
        """Verify out of stock products cannot be updated in the bag."""
        response = self.client.post(
            reverse("bag_update", args=[self.out_of_stock_product.pk]),
            {"quantity": 3}
        )
        bag = self.client.session.get("bag", {})

        self.assertEqual(response.status_code, 404)
        self.assertNotIn(str(self.out_of_stock_product.pk), bag)

    def test_cannot_update_zero_or_negative_quantity(self):
        """Verify zero and negative quantities are rejected."""
        self.client.post(
            reverse("bag_add", args=[self.active_product.pk])
        )
        for quantity in (0, -2):
            with self.subTest(quantity=quantity):
                self.client.post(
                    reverse("bag_update", args=[self.active_product.pk]),
                    {"quantity": quantity}
                )
                bag = self.client.session.get("bag", {})

                self.assertEqual(bag[str(self.active_product.pk)], 1)

    def test_cannot_update_non_numeric_or_missing_quantity(self):
        """Verify invalid quantity input
        is rejected without changing the bag."""
        self.client.post(
            reverse("bag_add", args=[self.active_product.pk])
        )

        for data in ({"quantity": "abc"}, {}):
            with self.subTest(data=data):
                response = self.client.post(
                    reverse("bag_update", args=[self.active_product.pk]),
                    data
                )

                bag = self.client.session.get("bag", {})

                self.assertEqual(response.status_code, 400)
                self.assertEqual(bag[str(self.active_product.pk)], 1)

    def test_cannot_update_quantity_above_stock(self):
        """Verify bag quantity cannot be updated above available stock."""
        self.client.post(
            reverse("bag_add", args=[self.active_product.pk])
        )
        self.client.post(
            reverse("bag_update", args=[self.active_product.pk]),
            {"quantity": 10}
        )
        bag = self.client.session.get("bag", {})

        self.assertEqual(
            bag[str(self.active_product.pk)],
            1
        )

    def test_cannot_update_product_not_in_bag(self):
        response = self.client.post(
            reverse("bag_update", args=[self.active_product.pk]),
            {"quantity": 3}
        )
        bag = self.client.session.get("bag", {})

        self.assertNotIn(
            str(self.active_product.pk),
            bag
        )
        self.assertEqual(response.status_code, 404)

    def test_empty_bag_returns_no_items_and_zero_total(self):
        """Verify an empty bag contains no items and has a zero total."""
        bag_details = get_bag_details({})
        self.assertEqual(bag_details, {'items': [], 'total': Decimal('0.00')})

    def test_bag_detail_page_returns_200(self):
        """Verify the shopping bag page returns HTTP 200."""
        response = self.client.get(reverse("bag_detail"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "bag/bag_detail.html")

    def test_bag_detail_context_contains_items_and_total(self):
        """Verify the bag page context contains items and the grand total."""
        self.client.post(
            reverse("bag_add", args=[self.active_product.pk])
        )
        response = self.client.get(reverse("bag_detail"))

        self.assertEqual(len(response.context["items"]), 1)
        self.assertEqual(response.context["total"], Decimal("500.00"))

    def test_bag_detail_displays_item_details(self):
        """Verify the bag page displays product name,
        price, quantity and subtotal."""
        self.client.post(
            reverse("bag_add", args=[self.active_product.pk])
        )
        self.client.post(
            reverse("bag_update", args=[self.active_product.pk]),
            {"quantity": 3},
        )

        response = self.client.get(reverse("bag_detail"))

        self.assertContains(response, self.active_product.name)
        self.assertContains(response, "500.00")
        self.assertContains(response, "3")
        self.assertContains(response, "1500.00")

    def test_bag_detail_displays_total(self):
        """Verify the bag page displays the overall shopping bag total."""
        self.client.post(
            reverse("bag_add", args=[self.active_product.pk])
        )
        self.client.post(
            reverse("bag_update", args=[self.active_product.pk]),
            {"quantity": 3}
        )
        response = self.client.get(reverse("bag_detail"))

        self.assertContains(response, "Total: 1500.00")

    def test_bag_detail_displays_product_image(self):
        """Verify the bag page displays the product image."""
        image = ProductImage.objects.create(
            product=self.active_product,
            image="products/test-kite.webp",
            is_primary=True,
        )
        self.client.post(
            reverse("bag_add", args=[self.active_product.pk])
        )
        response = self.client.get(reverse("bag_detail"))
        self.assertContains(
            response, image.image.url
        )

    def test_bag_detail_displays_fallback_image(self):
        """Verify the bag page displays
        a fallback when no product image exists."""
        self.client.post(
            reverse("bag_add", args=[self.active_product.pk])
        )
        response = self.client.get(reverse("bag_detail"))
        self.assertContains(
            response, "/static/images/default-image-fallback.webp"
        )

    def test_bag_detail_uses_first_image_when_no_primary_exists(self):
        """Verify the bag displays an image when none is marked primary."""
        image = ProductImage.objects.create(
            product=self.active_product,
            image="products/test-kite.webp",
            is_primary=False,
        )
        self.client.post(
            reverse("bag_add", args=[self.active_product.pk])
        )
        response = self.client.get(reverse("bag_detail"))
        self.assertContains(
            response, image.image.url
        )

    def test_out_of_stock_product_has_no_add_to_bag_form(self):
        """Verify out-of-stock products cannot be added from the PDP."""
        response = self.client.get(
            reverse("product_detail", args=[self.out_of_stock_product.pk])
        )
        url = reverse(
            "bag_add",
            args=[self.out_of_stock_product.pk]
        )
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, f'action="{url}"')

    def test_add_product_returns_json_response(self):
        """Verify adding a product returns JSON with updated quantity."""
        response = self.client.post(
            reverse("bag_add", args=[self.active_product.pk])
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/json")

        data = response.json()

        self.assertTrue(data["success"])
        self.assertEqual(data["quantity"], 1)

        self.assertEqual(
            self.client.session["bag"],
            {str(self.active_product.pk): 1},
        )

    def test_add_product_rejects_stock_limit(self):
        """Verify adding beyond stock returns an error."""
        session = self.client.session
        session["bag"] = {
            str(self.active_product.pk): self.active_product.stock
        }
        session.save()

        response = self.client.post(
            reverse("bag_add", args=[self.active_product.pk])
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            self.client.session["bag"][str(self.active_product.pk)],
            self.active_product.stock,
        )

    def test_update_product_returns_json_response(self):
        """Verify updating quantity returns the new quantity."""
        session = self.client.session
        session["bag"] = {str(self.active_product.pk): 1}
        session.save()

        response = self.client.post(
            reverse("bag_update", args=[self.active_product.pk]),
            {"quantity": 3},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["quantity"], 3)

    def test_update_rejects_quantity_exceeding_stock(self):
        """Verify quantity cannot exceed available stock."""
        session = self.client.session
        session["bag"] = {str(self.active_product.pk): 1}
        session.save()

        response = self.client.post(
            reverse("bag_update", args=[self.active_product.pk]),
            {"quantity": self.active_product.stock + 1},
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            self.client.session["bag"][str(self.active_product.pk)],
            1,
        )

    def test_update_rejects_zero_quantity(self):
        """Verify zero quantity is rejected."""
        session = self.client.session
        session["bag"] = {str(self.active_product.pk): 1}
        session.save()

        response = self.client.post(
            reverse("bag_update", args=[self.active_product.pk]),
            {"quantity": 0},
        )

        self.assertEqual(response.status_code, 400)

    def test_update_rejects_negative_quantity(self):
        """Verify negative quantity is rejected."""
        session = self.client.session
        session["bag"] = {str(self.active_product.pk): 1}
        session.save()

        response = self.client.post(
            reverse("bag_update", args=[self.active_product.pk]),
            {"quantity": -1},
        )

        self.assertEqual(response.status_code, 400)
