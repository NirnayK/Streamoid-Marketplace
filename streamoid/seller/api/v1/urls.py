from django.urls import path

from .views import SellerPostView

urlpatterns = [
    path("posts/", SellerPostView.as_view(), name="seller-post"),
]
