from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404

from products.models import Product
from .utils import get_bag_details


def bag_detail(request):
    """Display the shopping bag with items and total cost."""
    bag = request.session.get("bag", {})

    return render(
        request,
        "bag/bag_detail.html",
        get_bag_details(bag),
    )


def bag_add(request, product_id):
    """Handle adding a product to the shopping bag."""
    product = get_object_or_404(
        Product,
        pk=product_id,
        is_active=True,
        stock__gt=0
    )
    bag = request.session.get("bag", {})
    product_id_str = str(product_id)
    current_quantity = bag.get(product_id_str, 0)

    if current_quantity < product.stock:
        bag[product_id_str] = bag.get(product_id_str, 0) + 1

    request.session["bag"] = bag

    return HttpResponse(status=200)


def bag_update(request, product_id):
    """Handle updating a product quantity in the shopping bag."""
    product = get_object_or_404(
        Product,
        pk=product_id,
        is_active=True,
        stock__gt=0,
    )
    bag = request.session.get("bag", {})
    product_id_str = str(product_id)
    if product_id_str not in bag:
        return HttpResponse(status=404)

    try:
        quantity = int(request.POST.get("quantity"))
    except (ValueError, TypeError):
        return HttpResponse(status=400)

    if quantity > 0 and quantity <= product.stock:
        bag[product_id_str] = quantity
        request.session["bag"] = bag

    return HttpResponse(status=200)


def bag_remove(request, product_id):
    """Handle removing product items in the shopping bag."""
    bag = request.session.get("bag", {})
    product_id_str = str(product_id)
    bag.pop(product_id_str, None)

    request.session["bag"] = bag

    return HttpResponse(status=200)
