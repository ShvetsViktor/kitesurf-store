from decimal import Decimal

from products.models import Product


def get_bag_details(session_bag):
    """Calculate shopping bag items and totals."""
    items = []
    total = Decimal("0.00")
    for product_id, quantity in session_bag.items():
        product = Product.objects.get(pk=product_id)
        subtotal = product.price * quantity
        total += subtotal
        items.append(
            {
                "product": product,
                "quantity": quantity,
                "subtotal": subtotal,
            }
        )

    return {"items": items, "total": total}
