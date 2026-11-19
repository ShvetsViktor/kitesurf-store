from django.http import HttpResponse
from django.shortcuts import get_object_or_404

from products.models import Product


def bag_add(request, product_id):
    """Handle adding a product to the shopping bag."""
    get_object_or_404(Product, pk=product_id, is_active=True, stock__gt=0)
    bag = request.session.get("bag", {})
    product_id_str = str(product_id)
    bag[product_id_str] = bag.get(product_id_str, 0) + 1
    request.session["bag"] = bag

    return HttpResponse(status=200)


def bag_update(request, product_id):
    """Handle updating a product quantity in the shopping bag."""
    bag = request.session.get("bag", {})
    quantity = int(request.POST.get("quantity"))
    product_id_str = str(product_id)
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
