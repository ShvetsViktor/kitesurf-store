"""Tests for customer account functionality."""

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from allauth.account.models import EmailAddress


User = get_user_model()


class CustomerRegistrationTests(TestCase):
    """Test customer registration through django-allauth."""

    def test_signup_page_available_to_anonymous_user(self):
        """Anonymous visitors can access the registration page."""
        response = self.client.get(reverse("account_signup"))

        self.assertEqual(response.status_code, 200)

    def test_customer_can_register_with_valid_details(self):
        """Valid registration creates a customer account."""
        response = self.client.post(
            reverse("account_signup"),
            {
                "email": "customer@example.com",
                "password1": "SecureTestPassword123!",
                "password2": "SecureTestPassword123!",
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            User.objects.filter(email="customer@example.com").exists()
        )

    def test_duplicate_email_registration_is_rejected(self):
        """Duplicate registration must not create another user."""
        User.objects.create_user(
            username="existing",
            email="existing@example.com",
            password="SecureTestPassword123!",
        )

        response = self.client.post(
            reverse("account_signup"),
            {
                "email": "existing@example.com",
                "password1": "SecureTestPassword123!",
                "password2": "SecureTestPassword123!",
            },
        )

        self.assertEqual(
            User.objects.filter(email="existing@example.com").count(),
            1,
        )
        self.assertIn(response.status_code, (200, 302))

    def test_invalid_registration_does_not_create_account(self):
        """Invalid registration data does not create a user."""
        response = self.client.post(
            reverse("account_signup"),
            {
                "email": "invalid-email",
                "password1": "short",
                "password2": "different",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(User.objects.count(), 0)

    def test_new_customer_email_is_not_verified(self):
        """New accounts require email verification."""
        self.client.post(
            reverse("account_signup"),
            {
                "email": "customer@example.com",
                "password1": "SecureTestPassword123!",
                "password2": "SecureTestPassword123!",
            },
        )

        email = EmailAddress.objects.get(email="customer@example.com")

        self.assertFalse(email.verified)
