from django.urls import path

from .views import SellerFilesDetailView, SellerFilesView, SellerView

urlpatterns = [
    path("files/<int:file_id>/", SellerFilesDetailView.as_view(), name="seller-file-details"),
    path("files/", SellerFilesView.as_view(), name="seller-files"),
    path("", SellerView.as_view(), name="seller"),
]

app_name = "seller"
