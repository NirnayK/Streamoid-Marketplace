from django.urls import path

from marketplace.api.v1.views import MarketplaceTemplateDetailView, MarketplaceTemplateView

urlpatterns = [
    path("<int:marketplace_template_id>/", MarketplaceTemplateDetailView.as_view(), name="marketplace-details"),
    path("", MarketplaceTemplateView.as_view(), name="marketplace"),
]

app_name = "marketplace"
