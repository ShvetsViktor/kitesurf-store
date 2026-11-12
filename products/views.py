from django.shortcuts import render

from .models import Category, Product


def product_list(request):
    """Display active products with search and category filtering."""
    products = Product.objects.filter(
        is_active=True
    ).prefetch_related("images")

    categories = Category.objects.all()

    query = request.GET.get("q", "").strip()
    category = request.GET.get("category", "").strip()

    if query:
        products = products.filter(name__icontains=query)

    if category:
        products = products.filter(category__slug=category)

    return render(
        request,
        "products/product_list.html",
        {
            "products": products,
            "categories": categories,
            "query": query,
            "selected_category": category,
        },
    )
