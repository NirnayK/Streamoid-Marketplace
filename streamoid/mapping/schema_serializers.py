from core.serializers import BaseListResponseSerializer
from mapping.serializers import MappingsListSerializer


class MappingsListResponseSerializer(BaseListResponseSerializer):
    data = MappingsListSerializer(many=True)
