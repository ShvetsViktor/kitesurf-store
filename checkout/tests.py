from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase

from accounts.models import CustomerProfile
from checkout.models import Order, OrderItem
from products.models import Category, Product


class OrderModelTests(TestCase):
    """Test essential order behaviour."""

    def test_guest_order_defaults_to_pending(self):
        """A guest can have an order without a customer profile."""
        order = Order.objects.create(
            order_number="TEST-001",
            full_name="Guest Customer",
            email="guest@example.com",
            address_line_1="10 Test Street",
            city="Manchester",
            postcode="M1 1AA",
            order_total=Decimal("100.00"),
            delivery_cost=Decimal("0.00"),
            grand_total=Decimal("100.00"),
        )

        self.assertIsNone(order.customer)
        self.assertEqual(order.status, Order.Status.PENDING)

    def test_registered_order_links_to_customer_profile(self):
        """A registered customer's order references their profile."""
        user = get_user_model().objects.create_user(
            username="checkout_customer",
            email="customer@example.com",
            password="TestPassword123!",
        )
        profile = CustomerProfile.objects.get(user=user)

        order = Order.objects.create(
            customer=profile,
            order_number="TEST-002",
            full_name="Registered Customer",
            email=user.email,
            address_line_1="20 Test Street",
            city="Manchester",
            postcode="M1 2AB",
            order_total=Decimal("50.00"),
            delivery_cost=Decimal("0.00"),
            grand_total=Decimal("50.00"),
        )

        self.assertEqual(order.customer, profile)

    def test_order_item_preserves_purchase_details(self):
        """Order items retain their original names and prices."""
        category = Category.objects.create(
            name="Kites",
            slug="kites",
        )
        product = Product.objects.create(
            category=category,
            sku="KITE-001",
            name="Original Kite",
            description="Test kite",
            price=Decimal("450.00"),
            stock=5,
        )
        order = Order.objects.create(
            order_number="TEST-003",
            full_name="Guest Customer",
            email="guest@example.com",
            address_line_1="10 Test Street",
            city="Manchester",
            postcode="M1 1AA",
            order_total=Decimal("450.00"),
            delivery_cost=Decimal("0.00"),
            grand_total=Decimal("450.00"),
        )
        item = OrderItem.objects.create(
            order=order,
            product=product,
            product_name=product.name,
            quantity=1,
            price=product.price,
        )

        product.name = "Renamed Kite"
        product.price = Decimal("500.00")
        product.save()

        item.refresh_from_db()

        self.assertEqual(item.product_name, "Original Kite")
        self.assertEqual(item.price, Decimal("450.00"))
