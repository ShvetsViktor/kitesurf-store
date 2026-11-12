from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.db.models.deletion import ProtectedError
from django.test import TestCase
from django.urls import reverse

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


class ProductAdminTests(TestCase):
    """Test catalogue administration and access permissions."""

    def setUp(self):
        user_model = get_user_model()

        self.superuser = user_model.objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password="TestPassword123!",
        )

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

    def test_product_is_registered_in_admin(self):
        """Verify the product changelist is accessible."""
        self.client.force_login(self.superuser)

        response = self.client.get(
            reverse("admin:products_product_changelist")
        )

        self.assertEqual(response.status_code, 200)

    def test_category_is_registered_in_admin(self):
        """Verify the category changelist is accessible."""
        self.client.force_login(self.superuser)

        response = self.client.get(
            reverse("admin:products_category_changelist")
        )

        self.assertEqual(response.status_code, 200)

    def test_anonymous_user_cannot_access_product_admin(self):
        """Verify anonymous users are redirected to login."""
        response = self.client.get(
            reverse("admin:products_product_changelist")
        )

        self.assertEqual(response.status_code, 302)

    def test_non_staff_user_cannot_access_product_admin(self):
        """Verify non-staff users cannot access product administration."""
        user_model = get_user_model()

        user = user_model.objects.create_user(
            username="customer",
            password="TestPassword123!",
        )

        self.client.force_login(user)

        response = self.client.get(
            reverse("admin:products_product_changelist")
        )

        self.assertEqual(response.status_code, 302)

    def test_product_admin_displays_product(self):
        """Verify products appear in the admin changelist."""
        self.client.force_login(self.superuser)

        response = self.client.get(
            reverse("admin:products_product_changelist")
        )

        self.assertContains(response, self.product.name)

    def test_product_admin_has_image_inline(self):
        """Verify product images can be managed inline."""
        from django.contrib import admin

        product_admin = admin.site._registry[Product]

        self.assertTrue(
            any(
                inline.model is ProductImage
                for inline in product_admin.inlines
            )
        )

    def test_saving_product_preserves_primary_image(self):
        """Verify editing a product preserves its primary image."""
        image = ProductImage.objects.create(
            product=self.product,
            image="products/primary.jpg",
            is_primary=True,
        )

        self.client.force_login(self.superuser)

        response = self.client.post(
            reverse(
                "admin:products_product_change",
                args=[self.product.pk],
            ),
            {
                "category": self.category.pk,
                "sku": self.product.sku,
                "name": "Updated Test Kite",
                "description": self.product.description,
                "price": "100.00",
                "stock": "5",
                "is_active": "on",
                "images-TOTAL_FORMS": "1",
                "images-INITIAL_FORMS": "1",
                "images-MIN_NUM_FORMS": "0",
                "images-MAX_NUM_FORMS": "1000",
                "images-0-id": image.pk,
                "images-0-product": self.product.pk,
                "images-0-is_primary": "on",
            },
        )

        self.assertEqual(response.status_code, 302)

        image.refresh_from_db()
        self.product.refresh_from_db()

        self.assertTrue(image.is_primary)
        self.assertEqual(self.product.primary_image, image)
        self.assertEqual(self.product.name, "Updated Test Kite")

    def test_admin_rejects_multiple_primary_images(self):
        """Verify admin displays a validation error for two primary images."""
        first_image = ProductImage.objects.create(
            product=self.product,
            image="products/first.jpg",
            is_primary=True,
        )

        second_image = ProductImage.objects.create(
            product=self.product,
            image="products/second.jpg",
            is_primary=False,
        )

        self.client.force_login(self.superuser)

        response = self.client.post(
            reverse(
                "admin:products_product_change",
                args=[self.product.pk],
            ),
            {
                "category": self.category.pk,
                "sku": self.product.sku,
                "name": self.product.name,
                "description": self.product.description,
                "price": "100.00",
                "stock": "5",
                "is_active": "on",
                "images-TOTAL_FORMS": "2",
                "images-INITIAL_FORMS": "2",
                "images-MIN_NUM_FORMS": "0",
                "images-MAX_NUM_FORMS": "1000",
                "images-0-id": first_image.pk,
                "images-0-product": self.product.pk,
                "images-0-is_primary": "on",
                "images-1-id": second_image.pk,
                "images-1-product": self.product.pk,
                "images-1-is_primary": "on",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            "Only one primary image is allowed per product.",
        )

        first_image.refresh_from_db()
        second_image.refresh_from_db()

        self.assertTrue(first_image.is_primary)
        self.assertFalse(second_image.is_primary)

    def test_admin_can_switch_primary_image(self):
        """Verify admin can switch the primary image in one save."""
        first_image = ProductImage.objects.create(
            product=self.product,
            image="products/first.jpg",
            is_primary=True,
        )

        second_image = ProductImage.objects.create(
            product=self.product,
            image="products/second.jpg",
            is_primary=False,
        )

        self.client.force_login(self.superuser)

        response = self.client.post(
            reverse(
                "admin:products_product_change",
                args=[self.product.pk],
            ),
            {
                "category": self.category.pk,
                "sku": self.product.sku,
                "name": self.product.name,
                "description": self.product.description,
                "price": "100.00",
                "stock": "5",
                "is_active": "on",
                "images-TOTAL_FORMS": "2",
                "images-INITIAL_FORMS": "2",
                "images-MIN_NUM_FORMS": "0",
                "images-MAX_NUM_FORMS": "1000",
                "images-0-id": first_image.pk,
                "images-0-product": self.product.pk,
                "images-1-id": second_image.pk,
                "images-1-product": self.product.pk,
                "images-1-is_primary": "on",
            },
        )

        self.assertEqual(response.status_code, 302)

        first_image.refresh_from_db()
        second_image.refresh_from_db()

        self.assertFalse(first_image.is_primary)
        self.assertTrue(second_image.is_primary)
        self.assertEqual(self.product.primary_image, second_image)

    def test_admin_can_switch_primary_image_in_reverse_order(self):
        """Verify primary image switching works regardless of inline order."""
        first_image = ProductImage.objects.create(
            product=self.product,
            image="products/first.jpg",
            is_primary=False,
        )

        second_image = ProductImage.objects.create(
            product=self.product,
            image="products/second.jpg",
            is_primary=True,
        )

        self.client.force_login(self.superuser)

        response = self.client.post(
            reverse(
                "admin:products_product_change",
                args=[self.product.pk],
            ),
            {
                "category": self.category.pk,
                "sku": self.product.sku,
                "name": self.product.name,
                "description": self.product.description,
                "price": "100.00",
                "stock": "5",
                "is_active": "on",
                "images-TOTAL_FORMS": "2",
                "images-INITIAL_FORMS": "2",
                "images-MIN_NUM_FORMS": "0",
                "images-MAX_NUM_FORMS": "1000",
                "images-0-id": first_image.pk,
                "images-0-product": self.product.pk,
                "images-0-is_primary": "on",
                "images-1-id": second_image.pk,
                "images-1-product": self.product.pk,
            },
        )

        self.assertEqual(response.status_code, 302)

        first_image.refresh_from_db()
        second_image.refresh_from_db()

        self.assertTrue(first_image.is_primary)
        self.assertFalse(second_image.is_primary)
        self.assertEqual(self.product.primary_image, first_image)

    def test_admin_can_delete_primary_image(self):
        """Verify deleting a primary image preserves other images."""
        primary_image = ProductImage.objects.create(
            product=self.product,
            image="products/primary.jpg",
            is_primary=True,
        )

        secondary_image = ProductImage.objects.create(
            product=self.product,
            image="products/secondary.jpg",
            is_primary=False,
        )

        self.client.force_login(self.superuser)

        response = self.client.post(
            reverse(
                "admin:products_product_change",
                args=[self.product.pk],
            ),
            {
                "category": self.category.pk,
                "sku": self.product.sku,
                "name": self.product.name,
                "description": self.product.description,
                "price": "100.00",
                "stock": "5",
                "is_active": "on",
                "images-TOTAL_FORMS": "2",
                "images-INITIAL_FORMS": "2",
                "images-MIN_NUM_FORMS": "0",
                "images-MAX_NUM_FORMS": "1000",
                "images-0-id": primary_image.pk,
                "images-0-product": self.product.pk,
                "images-0-is_primary": "on",
                "images-0-DELETE": "on",
                "images-1-id": secondary_image.pk,
                "images-1-product": self.product.pk,
            },
        )

        self.assertEqual(response.status_code, 302)

        self.assertFalse(
            ProductImage.objects.filter(pk=primary_image.pk).exists()
        )

        self.assertTrue(
            ProductImage.objects.filter(pk=secondary_image.pk).exists()
        )

        self.assertIsNone(self.product.primary_image)

    def test_product_admin_displays_image_preview(self):
        """Verify the product admin displays an image thumbnail."""
        image = ProductImage.objects.create(
            product=self.product,
            image="products/test-image.jpg",
            is_primary=True,
        )

        self.client.force_login(self.superuser)

        response = self.client.get(
            reverse(
                "admin:products_product_change",
                args=[self.product.pk],
            )
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'width="100"')
        self.assertContains(response, image.image.url)


class ProductCatalogueViewTests(TestCase):
    """Test the public product catalogue page."""

    def test_product_catalogue_page_returns_200(self):
        """Verify visitors can access the catalogue page."""
        response = self.client.get(reverse("product_list"))

        self.assertEqual(response.status_code, 200)

    def test_product_catalogue_uses_correct_template(self):
        """Verify the catalogue uses the expected template."""
        response = self.client.get(reverse("product_list"))

        self.assertTemplateUsed(response, "products/product_list.html")


class ProductCatalogueQueryTests(TestCase):
    """Test product visibility in the public catalogue."""

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

    def test_active_products_are_in_catalogue(self):
        """Verify active products are included in the catalogue."""
        response = self.client.get(reverse("product_list"))

        self.assertIn(
            self.active_product,
            response.context["products"],
        )

    def test_inactive_products_are_excluded(self):
        """Verify inactive products are hidden from the catalogue."""
        response = self.client.get(reverse("product_list"))

        self.assertNotIn(
            self.inactive_product,
            response.context["products"],
        )

    def test_out_of_stock_products_remain_visible(self):
        """Verify active products with zero stock remain in the catalogue."""
        response = self.client.get(reverse("product_list"))

        self.assertIn(
            self.out_of_stock_product,
            response.context["products"],
        )

    def test_active_product_name_is_displayed(self):
        """Verify active product names appear in the catalogue."""
        response = self.client.get(reverse("product_list"))

        self.assertContains(response, self.active_product.name)

    def test_active_product_price_is_displayed(self):
        """Verify active product prices appear in the catalogue."""
        response = self.client.get(reverse("product_list"))

        self.assertContains(response, "500.00")

    def test_out_of_stock_product_is_labelled(self):
        """Verify unavailable products display an out-of-stock label."""
        response = self.client.get(reverse("product_list"))

        self.assertContains(response, "Out of stock")

    def test_product_without_image_displays_fallback(self):
        """Verify products without images display the fallback image."""
        response = self.client.get(reverse("product_list"))

        self.assertContains(
            response,
            "default-image-fallback.webp",
        )

    def test_product_primary_image_is_displayed(self):
        """Verify the catalogue displays a product's primary image."""
        ProductImage.objects.create(
            product=self.active_product,
            image="products/test-kite.webp",
            is_primary=True,
        )

        response = self.client.get(reverse("product_list"))

        self.assertContains(
            response,
            "products/test-kite.webp",
        )

    def test_search_products_by_name(self):
        """Verify catalogue search filters products by name."""
        response = self.client.get(
            reverse("product_list"),
            {"q": "Active Kite"},
        )

        products = response.context["products"]

        self.assertIn(self.active_product, products)
        self.assertNotIn(self.out_of_stock_product, products)
        self.assertNotIn(self.inactive_product, products)

    def test_search_is_case_insensitive(self):
        """Verify product search is case-insensitive."""
        response = self.client.get(
            reverse("product_list"),
            {"q": "active kite"},
        )

        self.assertIn(
            self.active_product,
            response.context["products"],
        )

    def test_search_ignores_surrounding_whitespace(self):
        """Verify surrounding whitespace is removed from search queries."""
        response = self.client.get(
            reverse("product_list"),
            {"q": "  Active Kite  "},
        )

        self.assertIn(
            self.active_product,
            response.context["products"],
        )

        self.assertNotIn(
            self.out_of_stock_product,
            response.context["products"],
        )

    def test_empty_search_returns_all_active_products(self):
        """Verify an empty search displays all active products."""
        response = self.client.get(
            reverse("product_list"),
            {"q": "   "},
        )

        products = response.context["products"]

        self.assertIn(self.active_product, products)
        self.assertIn(self.out_of_stock_product, products)
        self.assertNotIn(self.inactive_product, products)

    def test_catalogue_displays_search_form(self):
        """Verify the catalogue provides a product search form."""
        response = self.client.get(reverse("product_list"))

        self.assertContains(response, 'name="q"')
        self.assertContains(response, 'type="search"')
        self.assertContains(response, 'type="submit"')

    def test_search_query_remains_in_input(self):
        """Verify the search input retains the submitted query."""
        response = self.client.get(
            reverse("product_list"),
            {"q": "Active Kite"},
        )

        self.assertContains(response, 'value="Active Kite"')

    def test_filter_products_by_category(self):
        """Verify catalogue filters products by category slug."""
        boards = Category.objects.create(
            name="Boards",
            slug="boards",
        )

        board = Product.objects.create(
            category=boards,
            sku="BOARD-001",
            name="Test Board",
            description="Test description",
            price=Decimal("400.00"),
            stock=3,
            is_active=True,
        )

        response = self.client.get(
            reverse("product_list"),
            {"category": "boards"},
        )

        products = response.context["products"]

        self.assertIn(board, products)
        self.assertNotIn(self.active_product, products)
        self.assertNotIn(self.out_of_stock_product, products)
        self.assertNotIn(self.inactive_product, products)

    def test_search_and_filter_products_together(self):
        """Verify search and category filters work together."""
        boards = Category.objects.create(
            name="Boards",
            slug="boards",
        )

        matching_product = Product.objects.create(
            category=boards,
            sku="BOARD-KITE-001",
            name="Kite Board",
            description="Test description",
            price=Decimal("400.00"),
            stock=3,
            is_active=True,
        )

        response = self.client.get(
            reverse("product_list"),
            {
                "q": "kite",
                "category": "boards",
            },
        )

        products = response.context["products"]

        self.assertIn(matching_product, products)
        self.assertNotIn(self.active_product, products)
        self.assertNotIn(self.out_of_stock_product, products)
        self.assertNotIn(self.inactive_product, products)

    def test_filter_by_nonexistent_category(self):
        """Verify an unknown category returns no products."""
        response = self.client.get(
            reverse("product_list"),
            {"category": "nonexistent"},
        )

        products = response.context["products"]

        self.assertEqual(products.count(), 0)
        self.assertEqual(response.status_code, 200)

    def test_category_filter_context(self):
        """Verify categories and selected category are passed to template."""
        boards = Category.objects.create(
            name="Boards",
            slug="boards",
        )

        response = self.client.get(
            reverse("product_list"),
            {"category": "boards"},
        )

        self.assertIn(boards, response.context["categories"])
        self.assertEqual(
            response.context["selected_category"],
            "boards",
        )

    def test_selected_category_rendered_in_html(self):
        """Verify the selected category is preserved in the HTML."""
        Category.objects.create(
            name="Boards",
            slug="boards",
        )

        response = self.client.get(
            reverse("product_list"),
            {"category": "boards"},
        )

        self.assertContains(
            response,
            '<option value="boards" selected>Boards</option>',
            html=True,
        )

    def test_no_search_results_message(self):
        """Verify a helpful message appears when no products match."""
        response = self.client.get(
            reverse("product_list"),
            {"q": "nonexistentproduct123"},
        )

        self.assertContains(
            response,
            "No products match your search or filters.",
        )

    def test_empty_catalogue_message(self):
        """Verify a helpful message appears when catalogue is empty."""
        Product.objects.all().delete()

        response = self.client.get(reverse("product_list"))

        self.assertContains(
            response,
            "No products available.",
        )
