from rest_framework import serializers

from core.serializers import ModelSerializerBase
from marketplace.models import Marketplace, MarketplaceTempate


class MarketplaceSerializer(ModelSerializerBase):
    class Meta:
        model = Marketplace
        fields = ModelSerializerBase.Meta.fields + ("name",)


class MarketplaceTemplateListSerializer(ModelSerializerBase):
    marketplace = MarketplaceSerializer()

    class Meta:
        model = MarketplaceTempate
        fields = ModelSerializerBase.Meta.fields + ("marketplace", "template")


class MarketplaceTemplateSerializer(serializers.ModelSerializer):
    marketplace_id = serializers.IntegerField()
    template = serializers.JSONField()

    class Meta:
        model = MarketplaceTempate
        fields = ("marketplace", "template")

    def create(self, validated_data):
        marketplace_template = MarketplaceTempate.objects.create(**validated_data)
        return marketplace_template
