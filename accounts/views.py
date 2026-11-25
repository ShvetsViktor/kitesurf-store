from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.views.decorators.http import require_POST
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

            if not address.profile.delivery_addresses.filter(
                is_default=True
            ).exists():
                address.is_default = True

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


@login_required(login_url="account_login")
def address_delete(request, pk):
    """Allow customers to delete their own delivery addresses."""
    address = get_object_or_404(
        request.user.customer_profile.delivery_addresses,
        pk=pk,
    )

    if request.method == "POST":
        address.delete()

        messages.success(
            request,
            "Delivery address deleted successfully.",
        )

        return redirect("address_list")

    return render(
        request,
        "accounts/address_confirm_delete.html",
        {"address": address},
    )


@login_required(login_url="account_login")
@require_POST
def address_set_default(request, pk):
    """Set a customer's delivery address as default."""
    addresses = request.user.customer_profile.delivery_addresses

    with transaction.atomic():
        address = get_object_or_404(addresses, pk=pk)

        addresses.filter(is_default=True).update(is_default=False)

        address.is_default = True
        address.save(update_fields=["is_default"])

    messages.success(
        request,
        "Default delivery address updated successfully.",
    )

    return redirect("address_list")


@login_required(login_url="account_login")
def account_delete(request):
    """Allow customers to permanently delete their account."""
    if request.method == "POST":
        password = request.POST.get("password", "")

        if request.user.check_password(password):
            user = request.user

            logout(request)
            user.delete()

            messages.success(
                request,
                "Your account has been deleted successfully.",
            )

            return redirect("home")

        messages.error(
            request,
            "Incorrect password. Your account was not deleted.",
        )

    return render(
        request,
        "accounts/account_confirm_delete.html",
    )
