from django.contrib import admin

from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    """Display purchased items within an order."""

    model = OrderItem
    extra = 0
    readonly_fields = (
        "product",
        "product_name",
        "quantity",
        "price",
    )

    def has_add_permission(self, request, obj=None):
        """Prevent manually adding items to existing orders."""
        return False

    def has_delete_permission(self, request, obj=None):
        """Prevent deleting purchased items."""
        return False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """Manage orders and inspect payment information."""

    list_display = (
        "order_number",
        "full_name",
        "email",
        "status",
        "grand_total",
        "created_at",
    )
    list_filter = ("status", "created_at")
    search_fields = ("order_number", "full_name", "email")
    readonly_fields = (
        "order_number",
        "customer",
        "full_name",
        "email",
        "phone_number",
        "address_line_1",
        "address_line_2",
        "city",
        "county",
        "postcode",
        "order_total",
        "delivery_cost",
        "grand_total",
        "status",
        "stripe_session_id",
        "stripe_payment_intent_id",
        "created_at",
        "updated_at",
    )
    inlines = [OrderItemInline]

    def has_add_permission(self, request):
        """Orders must be created through checkout."""
        return False

    def has_delete_permission(self, request, obj=None):
        """Prevent deleting orders through Django Admin."""
        return False
