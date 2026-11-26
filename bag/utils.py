from decimal import Decimal

from products.models import Product


def get_bag_details(session_bag):
    """Validate shopping bag items and calculate current totals."""
    items = []
    total = Decimal("0.00")

    for product_id, quantity in session_bag.items():
        try:
            product = Product.objects.get(
                pk=product_id,
                is_active=True,
            )
        except (Product.DoesNotExist, ValueError, TypeError):
            raise ValueError("A product in your bag is unavailable.")

        if (
            type(quantity) is not int
            or quantity <= 0
            or quantity > product.stock
        ):
            raise ValueError(
                f"Invalid quantity or insufficient stock for {product.name}."
            )

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
