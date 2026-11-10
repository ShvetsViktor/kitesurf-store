from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import SimpleTestCase, TestCase


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
