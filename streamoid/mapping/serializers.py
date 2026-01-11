from rest_framework import serializers

from core.serializers import ModelSerializerBase
from mapping.models import Mappings
from marketplace.models import MarketplaceTempate
from marketplace.serializers import MarketplaceTemplateListSerializer
from seller.models import SellerFiles
from seller.serializers import SellerFilesSerializer


class MappingsListSerializer(ModelSerializerBase):
    marketplace_template = MarketplaceTemplateListSerializer(read_only=True)
    seller_file = SellerFilesSerializer(read_only=True)

    class Meta:
        model = Mappings
        fields = ModelSerializerBase.Meta.fields + ("marketplace_template", "seller_file", "mappings")


class MappingCreateSerializer(serializers.ModelSerializer):
    marketplace_template_id = serializers.IntegerField()
    seller_file_id = serializers.IntegerField()
    mappings = serializers.JSONField()

    class Meta:
        models = Mappings
        fields = ("marketplace_template_id", "seller_file_id", "mappings")

    def __init__(self, *args, **kwargs):
        super().__init__(self, *args, **kwargs)
        self._marketplace_template = None
        self._seller_file = None

    def validate_marketplace_template_id(self, marketplace_template_id):
        template = MarketplaceTempate.objects.filter(id=marketplace_template_id).last()
        if not template:
            return serializers.ValidationError("Invaid Marketplace Id")
        self._marketplace_template = template
        return marketplace_template_id

    def validate_seller_file_id(self, seller_file_id):
        seller_file = SellerFiles.objects.filter(id=seller_file_id).last()
        if not seller_file:
            return serializers.ValidationError("Invaid seller file Id")
        self.seller_file = seller_file
        return seller_file_id

    def validate_mappings(self, mappings):
        pass
