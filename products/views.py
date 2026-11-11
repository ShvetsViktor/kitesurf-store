from django.shortcuts import render


def product_list(request):
    """Display the public product catalogue."""
    return render(request, "products/product_list.html")
