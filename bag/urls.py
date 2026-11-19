from django.urls import path

from . import views

urlpatterns = [
    path("add/<int:product_id>/", views.bag_add, name="bag_add"),
    path("update/<int:product_id>/", views.bag_update, name="bag_update"),
]
