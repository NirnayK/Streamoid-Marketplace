from types import SimpleNamespace

from rest_framework import serializers

from core.custom_validation import CustomValidatior
from core.serializers import CreateBaseSerializer, DetailsBaseSerializer
from marketplace.models import Marketplace, MarketplaceTempate


class MarketplaceSerializer(DetailsBaseSerializer):
    class Meta:
        model = Marketplace
        fields = DetailsBaseSerializer.Meta.fields + ("name",)


class MarketplaceCreateSerializer(CreateBaseSerializer):
    class Meta:
        model = Marketplace
        fields = ("name",)


class MarketplaceTemplateListSerializer(DetailsBaseSerializer):
    marketplace = MarketplaceSerializer()

    class Meta:
        model = MarketplaceTempate
        fields = DetailsBaseSerializer.Meta.fields + ("marketplace", "template")


class MarketplaceTemplateSerializer(serializers.ModelSerializer):
    marketplace_id = serializers.IntegerField()
    template = serializers.JSONField()

    class Meta:
        model = MarketplaceTempate
        fields = ("marketplace_id", "template")

    def validate_template(self, template):
        validator = CustomValidatior(template=SimpleNamespace(template=template))
        serializer_class = validator.build()
        if serializer_class is None:
            raise serializers.ValidationError("Invalid template schema")
        return template
