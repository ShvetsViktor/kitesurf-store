from decimal import Decimal
from django.conf import settings
from django.contrib import messages
from django.db import transaction
from django.shortcuts import redirect, render
from django.urls import reverse
import stripe

from bag.utils import get_bag_details

from .forms import CheckoutForm
from .models import Order, OrderItem


def checkout(request):
    """Display checkout form and create pending orders."""
    bag = request.session.get("bag", {})

    if not bag:
        messages.error(request, "Your shopping bag is empty.")
        return redirect("bag_detail")

    try:
        bag_details = get_bag_details(bag)
    except ValueError:
        messages.error(
            request,
            "Some items in your bag are unavailable. "
            "Please review your shopping bag.",
        )
        return redirect("bag_detail")

    if request.method == "POST":
        form = CheckoutForm(request.POST)

        if form.is_valid():
            with transaction.atomic():
                order = form.save(commit=False)

                if request.user.is_authenticated:
                    order.customer = getattr(
                        request.user,
                        "customer_profile",
                        None,
                    )

                order.order_total = bag_details["total"]
                order.delivery_cost = Decimal("0.00")
                order.grand_total = order.order_total
                order.status = Order.Status.PENDING
                order.save()

                for item in bag_details["items"]:
                    OrderItem.objects.create(
                        order=order,
                        product=item["product"],
                        product_name=item["product"].name,
                        quantity=item["quantity"],
                        price=item["product"].price,
                    )

            stripe.api_key = settings.STRIPE_SECRET_KEY

            line_items = []

            for item in bag_details["items"]:
                product = item["product"]

                line_items.append(
                    {
                        "price_data": {
                            "currency": "gbp",
                            "product_data": {
                                "name": product.name,
                            },
                            "unit_amount": int(
                                product.price * 100
                            ),
                        },
                        "quantity": item["quantity"],
                    }
                )

            stripe_session = stripe.checkout.Session.create(
                mode="payment",
                line_items=line_items,
                client_reference_id=str(order.order_number),
                success_url=request.build_absolute_uri(
                    reverse("checkout_success")
                ),
                cancel_url=request.build_absolute_uri(
                    reverse("checkout_cancel")
                ),
            )

            order.stripe_session_id = stripe_session.id
            order.save(update_fields=["stripe_session_id"])

            return redirect(stripe_session.url)
    else:
        form = CheckoutForm()

    context = {
        "form": form,
        "items": bag_details["items"],
        "total": bag_details["total"],
    }

    return render(
        request,
        "checkout/checkout.html",
        context,
    )


def checkout_success(request):
    """Display the return page after Stripe Checkout."""
    return render(request, "checkout/success.html")


def checkout_cancel(request):
    """Display the page when Stripe Checkout is cancelled."""
    return render(request, "checkout/cancel.html")
