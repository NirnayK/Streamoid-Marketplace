from django.contrib import admin

from seller.models import Seller, SellerFiles


@admin.register(Seller)
class SellerAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "bucket_name", "created_at", "updated_at")
    search_fields = ("name", "bucket_name")
    readonly_fields = ("created_at", "updated_at")


@admin.register(SellerFiles)
class SellerFilesAdmin(admin.ModelAdmin):
    list_display = ("id", "seller", "name", "file_type", "rows_count", "created_at")
    list_filter = ("file_type",)
    search_fields = ("name", "path")
    readonly_fields = ("created_at", "updated_at")
