import stripe

from django.conf import settings
from django.db import transaction
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from .models import Order


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
                order.status = Order.Status.PAID
                order.save(update_fields=["status", "updated_at"])

    return HttpResponse(status=200)
