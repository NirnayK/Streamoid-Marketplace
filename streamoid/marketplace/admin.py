from django.contrib import admin

from marketplace.models import Marketplace, MarketplaceTempate


@admin.register(Marketplace)
class MarketplaceAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "created_at", "updated_at")
    search_fields = ("name",)
    readonly_fields = ("created_at", "updated_at")


@admin.register(MarketplaceTempate)
class MarketplaceTemplateAdmin(admin.ModelAdmin):
    list_display = ("id", "marketplace", "created_at", "updated_at")
    search_fields = ("marketplace__name",)
    readonly_fields = ("created_at", "updated_at")
