from django.contrib import messages
from django.shortcuts import redirect, render

from bag.utils import get_bag_details

from .forms import CheckoutForm


def checkout(request):
    """Display checkout form with validated shopping bag totals."""
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

    context = {
        "form": CheckoutForm(),
        "items": bag_details["items"],
        "total": bag_details["total"],
    }

    return render(
        request,
        "checkout/checkout.html",
        context,
    )
