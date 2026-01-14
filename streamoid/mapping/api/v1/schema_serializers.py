from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from core.serializers import BaseListResponseSerializer
from mapping.serializers import MappingsListSerializer


@extend_schema_field({"type": "array", "items": {"type": "object"}})
class MappingsField(serializers.JSONField):
    """Custom JSONField that renders as array of objects in OpenAPI schema."""

    pass


class MappingCreateRequestSerializer(serializers.Serializer):
    marketplace_template_id = serializers.IntegerField()
    seller_file_id = serializers.IntegerField()
    mappings = MappingsField()


class MappingsListResponseSerializer(BaseListResponseSerializer):
    data = MappingsListSerializer(many=True)
