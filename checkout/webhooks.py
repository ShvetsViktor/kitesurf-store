import stripe

from django.conf import settings
from django.db import transaction
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from .models import Order
from products.models import Product


@csrf_exempt
def stripe_webhook(request):
    """Verify Stripe webhook and update paid orders."""
    if request.method != "POST":
        return HttpResponse(status=405)

    try:
        event = stripe.Webhook.construct_event(
            request.body,
            request.headers.get("Stripe-Signature", ""),
            settings.STRIPE_WEBHOOK_SECRET,
        )
    except (ValueError, stripe.error.SignatureVerificationError):
        return HttpResponse(status=400)

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        if isinstance(session, stripe.StripeObject):
            session = session.to_dict()

        if session.get("payment_status") != "paid":
            return HttpResponse(status=200)

        with transaction.atomic():
            order = Order.objects.select_for_update().filter(
                stripe_session_id=session["id"],
            ).first()

            if order is None:
                return HttpResponse(status=400)

            if (
                session.get("currency") != "gbp"
                or session.get("amount_total")
                != int(order.grand_total * 100)
            ):
                return HttpResponse(status=400)

            if order.status == Order.Status.PENDING:
                required_stock = {}

                for item in order.items.all():
                    required_stock[item.product_id] = (
                        required_stock.get(item.product_id, 0) + item.quantity
                    )

                products = {
                    product.pk: product
                    for product in Product.objects.select_for_update().filter(
                        pk__in=required_stock
                    )
                }

                if any(
                    product_id not in products
                    or products[product_id].stock < quantity
                    for product_id, quantity in required_stock.items()
                ):
                    order.status = Order.Status.STOCK_ISSUE
                else:
                    for product_id, quantity in required_stock.items():
                        product = products[product_id]
                        product.stock -= quantity
                        product.save(update_fields=["stock"])

                    order.status = Order.Status.PAID

                order.save(update_fields=["status", "updated_at"])

    return HttpResponse(status=200)
