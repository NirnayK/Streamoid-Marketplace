from django.urls import path

from .views import SellerDetailView, SellerView

urlpatterns = [
    path("<int:file_id>/", SellerDetailView.as_view(), name="seller-details"),
    path("", SellerView.as_view(), name="seller"),
]

app_name = "seller"
