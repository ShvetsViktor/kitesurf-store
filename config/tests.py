from django.conf import settings
from django.test import SimpleTestCase


class DatabaseConfigurationTests(SimpleTestCase):

    def test_sqlite_database_is_used_for_tests(self):
        """Verify SQLite is used for the default test environment."""
        self.assertEqual(
            settings.DATABASES['default']['ENGINE'],
            'django.db.backends.sqlite3'
        )

    def test_sqlite_database_is_in_memory(self):
        """Verify SQLite uses an in-memory database."""
        self.assertEqual(
            settings.DATABASES['default']['NAME'],
            ':memory:'
        )
