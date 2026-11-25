from django.urls import path

from . import views


urlpatterns = [
    path("profile/", views.customer_profile, name="customer_profile"),
    path(
        "addresses/add/",
        views.address_create,
        name="address_create",
    ),
    path(
        "addresses/",
        views.address_list,
        name="address_list",
    ),
    path(
        "addresses/<int:pk>/edit/",
        views.address_update,
        name="address_update",
    ),
    path(
        "addresses/<int:pk>/delete/",
        views.address_delete,
        name="address_delete",
    ),
    path(
        "addresses/<int:pk>/set-default/",
        views.address_set_default,
        name="address_set_default",
    ),
]
