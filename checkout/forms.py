import re

from django import forms

from .models import Order


class CheckoutForm(forms.ModelForm):
    """Collect and validate customer checkout details."""

    class Meta:
        model = Order
        fields = (
            "full_name",
            "email",
            "phone_number",
            "address_line_1",
            "address_line_2",
            "city",
            "county",
            "postcode",
        )

    def clean_postcode(self):
        """Validate and normalise a UK postcode."""
        postcode = self.cleaned_data["postcode"].strip().upper()

        pattern = (
            r"^(GIR 0AA|"
            r"(?:[A-Z]{1,2}[0-9][A-Z0-9]?"
            r" ?[0-9][A-Z]{2}))$"
        )

        if not re.fullmatch(pattern, postcode):
            raise forms.ValidationError(
                "Enter a valid UK postcode."
            )

        return postcode
