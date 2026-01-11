from django.contrib import admin

from seller.models import Seller, SellerFiles


@admin.register(Seller)
class SellerAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "bucket_name", "created_at", "updated_at")
    search_fields = ("name", "bucket_name")
    readonly_fields = ("created_at", "updated_at")


@admin.register(SellerFiles)
class SellerFilesAdmin(admin.ModelAdmin):
    list_display = ("id", "seller", "name", "type", "rows_count", "created_at")
    list_filter = ("type", "created_at")
    search_fields = ("name", "path")
    readonly_fields = ("created_at", "updated_at")
