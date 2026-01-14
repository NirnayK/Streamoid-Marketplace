from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from core.serializers import BaseDetailResponseSerializer, BaseListResponseSerializer
from marketplace.serializers import MarketplaceSerializer, MarketplaceTemplateListSerializer


@extend_schema_field(OpenApiTypes.OBJECT)
class TemplateField(serializers.JSONField):
    """Custom JSONField that renders as object in OpenAPI schema."""

    pass


class MarketplaceTemplateCreateRequestSerializer(serializers.Serializer):
    template = TemplateField()


class MarketplaceTemplateListResponseSerializer(BaseListResponseSerializer):
    data = MarketplaceTemplateListSerializer(many=True)


class MarketplaceResponseSerializer(BaseDetailResponseSerializer):
    data = MarketplaceSerializer()


class MarketplaceListResponseSerializer(BaseListResponseSerializer):
    data = MarketplaceSerializer(many=True)
