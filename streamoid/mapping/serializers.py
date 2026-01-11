from core.serializers import ModelSerializerBase
from mapping.models import Mappings
from marketplace.serializers import MarketplaceTemplateListSerializer
from seller.serializers import SellerFilesSerializer


class MappingsListSerializer(ModelSerializerBase):
    marketplace_template = MarketplaceTemplateListSerializer(read_only=True)
    seller_file = SellerFilesSerializer(read_only=True)

    class Meta:
        model = Mappings
        fields = ModelSerializerBase.Meta.fields + ("marketplace_template", "seller_file", "mappings")
