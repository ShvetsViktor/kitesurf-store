from django.http import HttpResponse


def bag_add(request, product_id):
    """Handle adding a product to the shopping bag."""
    bag = request.session.get("bag", {})
    product_id_str = str(product_id)
    bag[product_id_str] = 1
    request.session["bag"] = bag

    return HttpResponse(status=200)
