from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .forms import CustomerProfileForm, DeliveryAddressForm


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


@login_required(login_url="account_login")
def address_create(request):
    """Allow authenticated customers to save a delivery address."""
    if request.method == "POST":
        form = DeliveryAddressForm(request.POST)

        if form.is_valid():
            address = form.save(commit=False)
            address.profile = request.user.customer_profile
            address.save()

            messages.success(
                request,
                "Delivery address added successfully.",
            )

            return redirect("address_list")
    else:
        form = DeliveryAddressForm()

    return render(
        request,
        "accounts/address_form.html",
        {"form": form},
    )


@login_required(login_url="account_login")
def address_list(request):
    """Display delivery addresses belonging to the customer."""
    addresses = request.user.customer_profile.delivery_addresses.all()

    return render(
        request,
        "accounts/address_list.html",
        {"addresses": addresses},
    )


@login_required(login_url="account_login")
def address_update(request, pk):
    """Allow customers to edit their own delivery addresses."""
    address = get_object_or_404(
        request.user.customer_profile.delivery_addresses,
        pk=pk,
    )

    if request.method == "POST":
        form = DeliveryAddressForm(request.POST, instance=address)

        if form.is_valid():
            form.save()

            messages.success(
                request,
                "Delivery address updated successfully.",
            )

            return redirect("address_list")
    else:
        form = DeliveryAddressForm(instance=address)

    return render(
        request,
        "accounts/address_form.html",
        {
            "form": form,
            "address": address,
        },
    )
