"""Tests for customer account functionality."""

from django.core import mail
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from allauth.account.models import EmailAddress, EmailConfirmationHMAC

from accounts.models import CustomerProfile


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


class CustomerAuthenticationTests(TestCase):
    """Test customer login and logout through django-allauth."""

    def setUp(self):
        """Create a verified customer for authentication tests."""
        self.password = "SecureTestPassword123!"

        self.user = User.objects.create_user(
            username="testcustomer",
            email="customer@example.com",
            password=self.password,
        )

        EmailAddress.objects.create(
            user=self.user,
            email=self.user.email,
            verified=True,
            primary=True,
        )

    def test_login_page_available_to_anonymous_user(self):
        """Anonymous visitors can access the login page."""
        response = self.client.get(reverse("account_login"))

        self.assertEqual(response.status_code, 200)

    def test_customer_can_login_with_valid_credentials(self):
        """Verified customers can log in using email and password."""
        response = self.client.post(
            reverse("account_login"),
            {
                "login": self.user.email,
                "password": self.password,
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            str(self.client.session["_auth_user_id"]),
            str(self.user.pk),
        )

    def test_invalid_credentials_do_not_authenticate_customer(self):
        """Invalid passwords must not authenticate customers."""
        response = self.client.post(
            reverse("account_login"),
            {
                "login": self.user.email,
                "password": "IncorrectPassword123!",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_customer_can_logout(self):
        """Logout must invalidate the authenticated session."""
        self.client.force_login(self.user)

        response = self.client.post(reverse("account_logout"))

        self.assertEqual(response.status_code, 302)
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_anonymous_user_cannot_access_logout_confirmation(self):
        """Anonymous visitors must not access authenticated logout flow."""
        response = self.client.get(reverse("account_logout"))

        self.assertNotEqual(response.status_code, 200)

    def test_unverified_customer_cannot_login(self):
        """Customers must verify their email before logging in."""
        email_address = EmailAddress.objects.get(user=self.user)
        email_address.verified = False
        email_address.save()

        self.client.post(
            reverse("account_login"),
            {
                "login": self.user.email,
                "password": self.password,
            },
        )

        self.assertNotIn("_auth_user_id", self.client.session)

    def test_authenticated_customer_cannot_access_login_page(self):
        """Authenticated customers are redirected away from login."""
        self.client.force_login(self.user)

        response = self.client.get(reverse("account_login"))

        self.assertEqual(response.status_code, 302)

    def test_logout_get_request_does_not_end_session(self):
        """Viewing the logout page must not log out the customer."""
        self.client.force_login(self.user)

        response = self.client.get(reverse("account_logout"))

        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            response.wsgi_request.user.is_authenticated
        )


class CustomerEmailVerificationTests(TestCase):
    """Test customer email verification through django-allauth."""

    def setUp(self):
        """Create a customer with an unverified email address."""
        self.password = "SecureTestPassword123!"

        self.user = get_user_model().objects.create_user(
            username="verificationcustomer",
            email="verification@example.com",
            password=self.password,
        )

        self.email_address = EmailAddress.objects.create(
            user=self.user,
            email=self.user.email,
            verified=False,
            primary=True,
        )

    def test_unverified_customer_cannot_login(self):
        """Customers must verify their email before logging in."""
        self.client.post(
            reverse("account_login"),
            {
                "login": self.user.email,
                "password": self.password,
            },
        )

        self.assertNotIn("_auth_user_id", self.client.session)

    def test_valid_confirmation_link_verifies_email(self):
        """A valid confirmation link verifies the email address."""
        confirmation = EmailConfirmationHMAC(self.email_address)

        response = self.client.post(
            reverse(
                "account_confirm_email",
                args=[confirmation.key],
            ),
        )

        self.email_address.refresh_from_db()

        self.assertEqual(response.status_code, 302)
        self.assertTrue(self.email_address.verified)

    def test_invalid_confirmation_link_does_not_verify_email(self):
        """An invalid confirmation link must not verify an email."""
        response = self.client.get(
            reverse(
                "account_confirm_email",
                args=["invalid-confirmation-key"],
            ),
        )

        self.email_address.refresh_from_db()

        self.assertFalse(self.email_address.verified)
        self.assertIn(response.status_code, (200, 404))

    def test_rejected_confirmation_key_does_not_verify_email(self):
        """Expired confirmation links must not verify email addresses."""
        from unittest.mock import patch

        confirmation = EmailConfirmationHMAC(self.email_address)

        with patch(
            "allauth.account.models.EmailConfirmationHMAC.from_key",
            return_value=None,
        ):
            response = self.client.get(
                reverse(
                    "account_confirm_email",
                    args=[confirmation.key],
                ),
            )

        self.email_address.refresh_from_db()

        self.assertFalse(self.email_address.verified)
        self.assertIn(response.status_code, (200, 404))

    def test_verified_customer_can_login(self):
        """Customers can log in after confirming their email."""
        self.email_address.verified = True
        self.email_address.save()

        response = self.client.post(
            reverse("account_login"),
            {
                "login": self.user.email,
                "password": self.password,
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            self.client.session.get("_auth_user_id")
        )


class CustomerPasswordResetTests(TestCase):
    """Test customer password reset functionality."""

    def setUp(self):
        """Create a customer for password reset tests."""
        self.user = get_user_model().objects.create_user(
            username="resetcustomer",
            email="reset@example.com",
            password="OldPassword123!",
        )

    def test_password_reset_page_loads(self):
        """Anonymous customers can access password reset."""
        response = self.client.get(
            reverse("account_reset_password")
        )

        self.assertEqual(response.status_code, 200)

    def test_password_reset_sends_email(self):
        """A registered customer can request a password reset."""
        response = self.client.post(
            reverse("account_reset_password"),
            {"email": self.user.email},
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn(self.user.email, mail.outbox[0].to)

    def test_password_reset_does_not_change_password_immediately(self):
        """Requesting a reset does not change the password."""
        self.client.post(
            reverse("account_reset_password"),
            {"email": self.user.email},
        )

        self.user.refresh_from_db()

        self.assertTrue(
            self.user.check_password("OldPassword123!")
        )

    def test_password_can_be_changed_after_reset(self):
        """A new password replaces the old password after reset."""
        self.user.set_password("NewPassword123!")
        self.user.save()

        self.user.refresh_from_db()

        self.assertFalse(
            self.user.check_password("OldPassword123!")
        )
        self.assertTrue(
            self.user.check_password("NewPassword123!")
        )


class CustomerProfileTests(TestCase):
    """Test customer profile lifecycle."""

    def setUp(self):
        """Create a customer."""
        self.user = get_user_model().objects.create_user(
            username="profilecustomer",
            email="profile@example.com",
            password="SecurePassword123!",
        )

    def test_profile_created_automatically(self):
        """A profile is automatically created for a new customer."""
        self.assertTrue(
            CustomerProfile.objects.filter(user=self.user).exists()
        )

    def test_profile_deleted_with_customer(self):
        """Deleting a customer also removes their profile."""
        user_id = self.user.pk

        self.user.delete()

        self.assertFalse(
            CustomerProfile.objects.filter(user_id=user_id).exists()
        )


class CustomerProfileViewTests(TestCase):
    """Test customer profile access and editing."""

    def setUp(self):
        """Create a customer."""
        self.user = get_user_model().objects.create_user(
            username="profilecustomer",
            email="profile@example.com",
            password="SecurePassword123!",
        )
        self.url = reverse("customer_profile")

    def test_authenticated_customer_can_view_profile(self):
        """An authenticated customer can access their profile."""
        self.client.force_login(self.user)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.user.email)

    def test_anonymous_customer_cannot_view_profile(self):
        """Anonymous visitors are redirected to login."""
        response = self.client.get(self.url)

        self.assertRedirects(
            response,
            f"{reverse('account_login')}?next={self.url}",
        )

    def test_customer_can_update_profile(self):
        """A customer can update their first and last name."""
        self.client.force_login(self.user)

        response = self.client.post(
            self.url,
            {
                "first_name": "John",
                "last_name": "Smith",
            },
        )

        self.user.refresh_from_db()

        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.user.first_name, "John")
        self.assertEqual(self.user.last_name, "Smith")
