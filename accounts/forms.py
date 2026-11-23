from django import forms
from django.contrib.auth import get_user_model


class CustomerProfileForm(forms.ModelForm):
    """Allow customers to update their personal information."""

    class Meta:
        model = get_user_model()
        fields = ["first_name", "last_name"]
