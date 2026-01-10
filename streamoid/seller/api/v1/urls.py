from django.urls import path

from .views import SellerView

urlpatterns = [
    path("<int:file_id>/", SellerView.as_view(), name="seller-details"),
    path("", SellerView.as_view(), name="seller"),
]

app_name = "seller"
