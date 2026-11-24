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
]
