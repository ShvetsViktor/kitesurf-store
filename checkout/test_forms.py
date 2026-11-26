from django.test import TestCase

from checkout.forms import CheckoutForm


class CheckoutFormTests(TestCase):
    """Test checkout form validation."""

    def setUp(self):
        self.valid_data = {
            "full_name": "Test Customer",
            "email": "customer@example.com",
            "phone_number": "07123456789",
            "address_line_1": "10 Test Street",
            "address_line_2": "",
            "city": "Manchester",
            "county": "",
            "postcode": "M1 1AA",
        }

    def test_valid_checkout_form(self):
        """Accept valid customer and UK delivery details."""
        form = CheckoutForm(data=self.valid_data)

        self.assertTrue(form.is_valid(), form.errors)

    def test_required_fields(self):
        """Reject missing essential checkout information."""
        required_fields = (
            "full_name",
            "email",
            "address_line_1",
            "city",
            "postcode",
        )

        for field in required_fields:
            with self.subTest(field=field):
                data = self.valid_data.copy()
                data[field] = ""

                form = CheckoutForm(data=data)

                self.assertFalse(form.is_valid())
                self.assertIn(field, form.errors)

    def test_invalid_email(self):
        """Reject invalid email addresses."""
        data = self.valid_data.copy()
        data["email"] = "invalid-email"

        form = CheckoutForm(data=data)

        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)

    def test_invalid_uk_postcode(self):
        """Reject invalid UK postcodes."""
        data = self.valid_data.copy()
        data["postcode"] = "INVALID"

        form = CheckoutForm(data=data)

        self.assertFalse(form.is_valid())
        self.assertIn("postcode", form.errors)

    def test_optional_fields(self):
        """Allow optional address and contact fields to be empty."""
        data = self.valid_data.copy()
        data["phone_number"] = ""
        data["address_line_2"] = ""
        data["county"] = ""

        form = CheckoutForm(data=data)

        self.assertTrue(form.is_valid(), form.errors)
