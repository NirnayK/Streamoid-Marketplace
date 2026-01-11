from django.contrib import admin

from mapping.models import Mappings


@admin.register(Mappings)
class MappingsAdmin(admin.ModelAdmin):
    list_display = ("id", "marketplace_template", "seller_file", "created_at", "updated_at")
    list_filter = ("marketplace_template", "seller_file", "created_at")
    list_select_related = ("marketplace_template", "seller_file", "marketplace_template__marketplace")
    search_fields = (
        "marketplace_template__marketplace__name",
        "seller_file__name",
        "seller_file__path",
    )
    readonly_fields = ("created_at", "updated_at")
