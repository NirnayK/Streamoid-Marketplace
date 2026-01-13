from django.urls import path

from .views import SellerFilesDetailView, SellerFilesView, SellerView

urlpatterns = [
    path("files/<int:file_id>/", SellerFilesDetailView.as_view(), name="seller-details"),
    path("files/", SellerFilesView.as_view(), name="seller"),
    path("", SellerView.as_view(), name="seller-create"),
]

app_name = "seller"
