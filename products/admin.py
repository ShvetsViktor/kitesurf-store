from django.core.exceptions import ValidationError
from django.contrib import admin
from django.forms.models import BaseInlineFormSet

from .models import Category, Product, ProductImage


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Manage product categories."""

    list_display = ("name", "slug")
    search_fields = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}


class ProductImageInlineFormSet(BaseInlineFormSet):
    """Ensure that each product has at most one primary image."""

    def clean(self):
        super().clean()

        if any(self.errors):
            return

        primary_count = 0

        for form in self.forms:
            if not form.cleaned_data:
                continue

            if form.cleaned_data.get("DELETE"):
                continue

            if form.cleaned_data.get("is_primary"):
                primary_count += 1

        if primary_count > 1:
            raise ValidationError(
                "Only one primary image is allowed per product."
            )


class ProductImageInline(admin.TabularInline):
    """Manage product images within the product form."""

    model = ProductImage
    formset = ProductImageInlineFormSet
    extra = 1


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """Manage products and their images."""

    list_display = (
        "name",
        "sku",
        "category",
        "price",
        "stock",
        "is_active",
    )
    list_filter = ("category", "is_active")
    search_fields = ("name", "sku")
    list_editable = ("price", "stock", "is_active")
    inlines = (ProductImageInline,)

    def save_formset(self, request, form, formset, change):
        """Save images without violating the primary image constraint."""
        if formset.model is ProductImage:
            instances = formset.save(commit=False)

            primary_image = next(
                (
                    instance
                    for instance in instances
                    if instance.is_primary
                ),
                None,
            )

            if primary_image is not None:
                ProductImage.objects.filter(
                    product=form.instance,
                    is_primary=True,
                ).exclude(
                    pk=primary_image.pk,
                ).update(is_primary=False)

            for obj in formset.deleted_objects:
                obj.delete()

            for instance in instances:
                instance.save()

            formset.save_m2m()
        else:
            super().save_formset(request, form, formset, change)
