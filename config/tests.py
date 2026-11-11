from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import SimpleTestCase, TestCase
from django.urls import reverse


class DatabaseConfigurationTests(SimpleTestCase):
    """Verify the SQLite test database configuration."""

    def test_sqlite_database_is_used_for_tests(self):
        """Verify SQLite is the default test database."""
        self.assertEqual(
            settings.DATABASES['default']['ENGINE'],
            'django.db.backends.sqlite3'
        )

    def test_sqlite_database_is_in_memory(self):
        """Verify SQLite uses an in-memory test database."""
        database_name = settings.DATABASES['default']['NAME']

        self.assertTrue(
            database_name == ':memory:'
            or (
                database_name.startswith('file:memorydb_')
                and 'mode=memory' in database_name
            )
        )


class DatabaseIsolationTests(TestCase):
    """Verify database operations and test isolation."""

    def test_user_creation(self):
        """Verify a user can be created in the test database."""
        User = get_user_model()

        User.objects.create_user(
            username='test_user',
            password='TestPassword123!'
        )

        self.assertTrue(
            User.objects.filter(username='test_user').exists()
        )

    def test_database_starts_without_test_user(self):
        """Verify each test starts without data from other tests."""
        User = get_user_model()

        self.assertFalse(
            User.objects.filter(username='test_user').exists()
        )


class HomePageTests(TestCase):
    """Tests for the public homepage."""

    def test_homepage_returns_200(self):
        """The homepage should be accessible to anonymous visitors."""
        response = self.client.get(reverse('home'))

        self.assertEqual(response.status_code, 200)

    def test_homepage_uses_base_template(self):
        """The homepage should inherit the shared base template."""
        response = self.client.get(reverse('home'))

        self.assertTemplateUsed(response, 'base.html')

    def test_homepage_contains_navigation(self):
        """The homepage should contain the main navigation."""
        response = self.client.get(reverse('home'))

        self.assertContains(response, '<nav', html=False)
        self.assertContains(response, 'Main navigation')

    def test_homepage_contains_footer(self):
        """The homepage should contain the shared footer."""
        response = self.client.get(reverse('home'))

        self.assertContains(response, '<footer', html=False)
        self.assertContains(response, 'KiteSurf Store')

    def test_homepage_contains_mobile_navigation_toggle(self):
        """The homepage should provide a Bootstrap mobile navigation toggle."""
        response = self.client.get(reverse('home'))

        self.assertContains(response, 'navbar-toggler')
        self.assertContains(response, 'data-bs-toggle="collapse"')

    def test_homepage_contains_brand_logos(self):
        """The header should contain desktop and mobile brand logos."""
        response = self.client.get(reverse('home'))

        self.assertContains(response, 'images/logo.webp')
        self.assertContains(response, 'images/logo-compact.webp')
        self.assertContains(response, 'alt="KiteSurf Store"')
