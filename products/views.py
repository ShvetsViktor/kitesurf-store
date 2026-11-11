from django.shortcuts import render

from .models import Product


def product_list(request):
    """Display all active products in the public catalogue."""
    products = Product.objects.filter(
        is_active=True
    ).prefetch_related("images")

    return render(
        request,
        "products/product_list.html",
        {"products": products},
    )
