from django.urls import path

from mapping.api.v1.views import MappingsDetailView, MappingsView

urlpatterns = [
    path("<int:mapping_id>/", MappingsDetailView.as_view(), name="mapping-details"),
    path("", MappingsView.as_view(), name="mapping"),
]

app_name = "mapping"
