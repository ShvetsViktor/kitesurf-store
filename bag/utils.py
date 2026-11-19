from products.models import Product


def get_bag_details(session_bag):
    """Calculate shopping bag items and totals."""
    items = []
    for product_id, quantity in session_bag.items():
        product = Product.objects.get(pk=product_id)
        subtotal = product.price * quantity
        items.append(
            {
                "product": product,
                "quantity": quantity,
                "subtotal": subtotal,
            }
        )

    return {"items": items, "total": 0}
