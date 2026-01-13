from rest_framework import serializers

from core.serializers import BaseDetailResponseSerializer, BaseListResponseSerializer
from marketplace.serializers import MarketplaceSerializer, MarketplaceTemplateListSerializer


class MarketplaceTemplateCreateRequestSerializer(serializers.Serializer):
    template = serializers.JSONField()


class MarketplaceTemplateListResponseSerializer(BaseListResponseSerializer):
    data = MarketplaceTemplateListSerializer(many=True)


class MarketplaceResponseSerializer(BaseDetailResponseSerializer):
    data = MarketplaceSerializer()
