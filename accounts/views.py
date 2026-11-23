from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .forms import CustomerProfileForm


@login_required(login_url="account_login")
def customer_profile(request):
    """Display and update the authenticated customer's profile."""
    if request.method == "POST":
        form = CustomerProfileForm(request.POST, instance=request.user)

        if form.is_valid():
            form.save()
            messages.success(request, "Your profile has been updated.")
            return redirect("customer_profile")
    else:
        form = CustomerProfileForm(instance=request.user)

    return render(
        request,
        "accounts/profile.html",
        {"form": form},
    )
