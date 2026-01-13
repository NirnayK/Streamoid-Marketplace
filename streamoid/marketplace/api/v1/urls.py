from django.urls import path

from marketplace.api.v1.views import (
    MarketplaceTemplateDetailView,
    MarketplaceTemplateView,
    MarketplaceView,
)

urlpatterns = [
    path(
        "templates/<int:marketplace_template_id>/",
        MarketplaceTemplateDetailView.as_view(),
        name="marketplace-details",
    ),
    path("templates/", MarketplaceTemplateView.as_view(), name="marketplace"),
    path("", MarketplaceView.as_view(), name="marketplace-create"),
]

app_name = "marketplace"
