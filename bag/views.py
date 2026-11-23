from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404
from django.views.decorators.http import require_POST

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


@require_POST
def bag_add(request, product_id):
    """Add an available product to the session shopping bag."""
    product = get_object_or_404(
        Product,
        pk=product_id,
        is_active=True,
        stock__gt=0,
    )

    bag = request.session.get("bag", {})
    product_id_str = str(product_id)

    current_quantity = bag.get(product_id_str, 0)

    if current_quantity >= product.stock:
        return JsonResponse(
            {"success": False, "error": "Insufficient stock."},
            status=400,
        )

    bag[product_id_str] = current_quantity + 1
    request.session["bag"] = bag

    return JsonResponse({
        "success": True,
        "quantity": bag.get(product_id_str, 0),
        "bag_count": sum(bag.values()),
    })


@require_POST
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
        return JsonResponse(
            {"success": False, "error": "Invalid quantity."},
            status=400,
        )

    if quantity <= 0 or quantity > product.stock:
        return JsonResponse(
            {"success": False, "error": "Invalid quantity."},
            status=400,
        )

    bag[product_id_str] = quantity
    request.session["bag"] = bag

    bag_details = get_bag_details(bag)

    return JsonResponse({
        "success": True,
        "quantity": quantity,
        "subtotal": str(product.price * quantity),
        "total": str(bag_details["total"]),
        "bag_count": sum(bag.values()),
    })


@require_POST
def bag_remove(request, product_id):
    """Remove a product from the shopping bag."""
    bag = request.session.get("bag", {})
    bag.pop(str(product_id), None)
    request.session["bag"] = bag

    bag_details = get_bag_details(bag)

    return JsonResponse({
        "success": True,
        "total": str(bag_details["total"]),
        "bag_count": sum(bag.values()),
    })
