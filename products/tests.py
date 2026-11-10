from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.db.models.deletion import ProtectedError
from django.test import TestCase

from .models import Category, Product, ProductImage


class CategoryModelTests(TestCase):
    """Test category creation, uniqueness and deletion protection."""

    def setUp(self):
        self.category = Category.objects.create(
            name="Kites",
            slug="kites",
        )

    def test_category_string_representation(self):
        """Verify the category displays its name."""
        self.assertEqual(str(self.category), "Kites")

    def test_category_name_must_be_unique(self):
        """Verify duplicate category names are rejected."""
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Category.objects.create(
                    name="Kites",
                    slug="different-slug",
                )

    def test_category_slug_must_be_unique(self):
        """Verify duplicate category slugs are rejected."""
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Category.objects.create(
                    name="Different Category",
                    slug="kites",
                )

    def test_category_with_products_cannot_be_deleted(self):
        """Verify PROTECT prevents deleting a populated category."""
        Product.objects.create(
            category=self.category,
            sku="KITE-001",
            name="Test Kite",
            description="Test description",
            price=Decimal("100.00"),
            stock=1,
        )

        with self.assertRaises(ProtectedError):
            self.category.delete()


class ProductModelTests(TestCase):
    """Test product validation, availability and relationships."""

    def setUp(self):
        self.category = Category.objects.create(
            name="Kites",
            slug="kites",
        )

        self.product = Product.objects.create(
            category=self.category,
            sku="KITE-001",
            name="Test Kite",
            description="Test description",
            price=Decimal("100.00"),
            stock=5,
        )

    def test_product_string_representation(self):
        """Verify the product displays its name."""
        self.assertEqual(str(self.product), "Test Kite")

    def test_product_sku_must_be_unique(self):
        """Verify duplicate SKUs are rejected."""
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Product.objects.create(
                    category=self.category,
                    sku="KITE-001",
                    name="Another Kite",
                    description="Test description",
                    price=Decimal("200.00"),
                )

    def test_product_price_must_be_positive(self):
        """Verify zero and negative prices are rejected."""
        for price in [Decimal("0.00"), Decimal("-1.00")]:
            with self.subTest(price=price):
                with self.assertRaises(IntegrityError):
                    with transaction.atomic():
                        Product.objects.create(
                            category=self.category,
                            sku=f"INVALID-{price}",
                            name="Invalid Product",
                            description="Test description",
                            price=price,
                        )

    def test_product_is_available(self):
        """Verify active products with stock are available."""
        self.assertTrue(self.product.is_available)

    def test_out_of_stock_product_is_unavailable(self):
        """Verify products with zero stock are unavailable."""
        self.product.stock = 0

        self.assertFalse(self.product.is_available)

    def test_inactive_product_is_unavailable(self):
        """Verify inactive products are unavailable."""
        self.product.is_active = False

        self.assertFalse(self.product.is_available)

    def test_product_stock_cannot_be_negative(self):
        """Verify negative stock values are rejected."""
        self.product.stock = -1

        with self.assertRaises(ValidationError):
            self.product.full_clean()

    def test_product_without_category_is_rejected(self):
        """Verify every product must belong to a category."""
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Product.objects.create(
                    sku="KITE-002",
                    name="No Category",
                    description="Test description",
                    price=Decimal("100.00"),
                )


class ProductImageModelTests(TestCase):
    """Test product images and primary image constraints."""

    def setUp(self):
        self.category = Category.objects.create(
            name="Kites",
            slug="kites",
        )

        self.product = Product.objects.create(
            category=self.category,
            sku="KITE-001",
            name="Test Kite",
            description="Test description",
            price=Decimal("100.00"),
        )

    def test_product_can_have_multiple_images(self):
        """Verify a product supports multiple images."""
        ProductImage.objects.create(
            product=self.product,
            image="products/image1.jpg",
        )

        ProductImage.objects.create(
            product=self.product,
            image="products/image2.jpg",
        )

        self.assertEqual(self.product.images.count(), 2)

    def test_primary_image_property(self):
        """Verify the primary image is returned."""
        image = ProductImage.objects.create(
            product=self.product,
            image="products/primary.jpg",
            is_primary=True,
        )

        self.assertEqual(self.product.primary_image, image)

    def test_only_one_primary_image_is_allowed(self):
        """Verify a product cannot have multiple primary images."""
        ProductImage.objects.create(
            product=self.product,
            image="products/primary1.jpg",
            is_primary=True,
        )

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                ProductImage.objects.create(
                    product=self.product,
                    image="products/primary2.jpg",
                    is_primary=True,
                )

    def test_deleting_product_removes_image_records(self):
        """Verify CASCADE removes related image records."""
        ProductImage.objects.create(
            product=self.product,
            image="products/image.jpg",
        )

        self.product.delete()

        self.assertEqual(ProductImage.objects.count(), 0)
