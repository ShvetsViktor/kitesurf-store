import re

from django import forms
from django.contrib.auth import get_user_model

from .models import DeliveryAddress


class CustomerProfileForm(forms.ModelForm):
    """Allow customers to update their personal information."""

    class Meta:
        model = get_user_model()
        fields = ["first_name", "last_name"]


class DeliveryAddressForm(forms.ModelForm):
    """Validate customer delivery address information."""

    class Meta:
        model = DeliveryAddress
        fields = [
            "full_name",
            "address_line_1",
            "address_line_2",
            "city",
            "county",
            "postcode",
            "phone_number",
        ]

    def clean_postcode(self):
        """Validate and normalise a UK postcode."""
        postcode = self.cleaned_data["postcode"].strip().upper()
        postcode = re.sub(r"\s+", "", postcode)

        pattern = (
            r"^(GIR0AA|"
            r"(?:[A-Z]{1,2}[0-9][A-Z0-9]?)"
            r"[0-9][A-Z]{2})$"
        )

        if not re.fullmatch(pattern, postcode):
            raise forms.ValidationError(
                "Enter a valid UK postcode."
            )

        return f"{postcode[:-3]} {postcode[-3:]}"
