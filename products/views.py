from django.shortcuts import render

from .models import Product


def product_list(request):
    """Display active products and support searching by name."""
    products = Product.objects.filter(
        is_active=True
    ).prefetch_related("images")

    query = request.GET.get("q", "").strip()

    if query:
        products = products.filter(name__icontains=query)

    return render(
        request,
        "products/product_list.html",
        {"products": products},
    )
