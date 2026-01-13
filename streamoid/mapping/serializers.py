from rest_framework import serializers

from core.file_validation import validate_file
from core.serializers import DetailsBaseSerializer
from mapping.models import Mappings
from marketplace.models import MarketplaceTempate
from marketplace.serializers import MarketplaceTemplateListSerializer
from seller.models import SellerFiles
from seller.serializers import SellerFilesSerializer


class MappingsListSerializer(DetailsBaseSerializer):
    marketplace_template = MarketplaceTemplateListSerializer(read_only=True)
    seller_file = SellerFilesSerializer(read_only=True)

    class Meta:
        model = Mappings
        fields = DetailsBaseSerializer.Meta.fields + (
            "marketplace_template",
            "seller_file",
            "mappings",
            "evaluation_status",
        )


class MappingCreateSerializer(serializers.ModelSerializer):
    marketplace_template_id = serializers.IntegerField()
    seller_file_id = serializers.IntegerField()
    mappings = serializers.JSONField()

    class Meta:
        model = Mappings
        fields = ("marketplace_template_id", "seller_file_id", "mappings")

    def __init__(self, *args, **kwargs):
        super().__init__(self, *args, **kwargs)
        self._marketplace_template = None
        self._seller_file = None

    def validate(self, attrs):
        attrs = super().validate(attrs)
        template = self._marketplace_template
        seller_file = self._seller_file
        if not template or not seller_file:
            return attrs
        validate_file(template, attrs.get("mappings"), seller_file.headers, seller_file.sample_rows)
        return attrs

    def validate_marketplace_template_id(self, marketplace_template_id):
        template = MarketplaceTempate.objects.filter(id=marketplace_template_id).last()
        if not template:
            raise serializers.ValidationError("Invaid Marketplace Id")
        self._marketplace_template = template
        return marketplace_template_id

    def validate_seller_file_id(self, seller_file_id):
        seller_file = SellerFiles.objects.filter(id=seller_file_id).last()
        if not seller_file:
            raise serializers.ValidationError("Invaid seller file Id")
        self._seller_file = seller_file
        return seller_file_id

    def _validate_mappings_list(self, mappings):
        if not isinstance(mappings, list):
            raise serializers.ValidationError("Mappings must be a list.")

    def _validate_mapping_dict(self, mapping, index):
        if not isinstance(mapping, dict):
            raise serializers.ValidationError(f"Mapping at index {index} must be an object.")

    def _extract_mapping_keys(self, mapping, index):
        seller_key = mapping.get("seller")
        marketplace_key = mapping.get("marketplace")
        if not seller_key or not marketplace_key:
            raise serializers.ValidationError(
                f"Mapping at index {index} must include 'seller' and 'marketplace' keys."
            )
        return seller_key, marketplace_key

    def _validate_seller_header(self, seller_key, seller_headers):
        if seller_key not in seller_headers:
            raise serializers.ValidationError(f"Seller header '{seller_key}' is not in the seller file.")

    def _validate_marketplace_key(self, marketplace_key, template_keys):
        if marketplace_key not in template_keys:
            raise serializers.ValidationError(
                f"Marketplace key '{marketplace_key}' is not in the marketplace template."
            )

    def _validate_unique_seller(self, seller_key, seen_seller):
        if seller_key in seen_seller:
            raise serializers.ValidationError(f"Seller header '{seller_key}' is mapped more than once.")

    def _allows_multiple(self, marketplace_key, template_rules):
        rules = template_rules.get(marketplace_key) or {}
        return (rules.get("type") or "").lower() in {"array", "list"}

    def _validate_unique_marketplace(self, marketplace_key, seen_marketplace, template_rules):
        if marketplace_key in seen_marketplace and not self._allows_multiple(marketplace_key, template_rules):
            raise serializers.ValidationError(f"Marketplace key '{marketplace_key}' is mapped more than once.")

    def _validate_mapping_item(
        self, mapping, index, template_rules, template_keys, seller_headers, seen_seller, seen_marketplace
    ):
        self._validate_mapping_dict(mapping, index)
        seller_key, marketplace_key = self._extract_mapping_keys(mapping, index)
        self._validate_seller_header(seller_key, seller_headers)
        self._validate_marketplace_key(marketplace_key, template_keys)
        self._validate_unique_seller(seller_key, seen_seller)
        self._validate_unique_marketplace(marketplace_key, seen_marketplace, template_rules)
        return seller_key, marketplace_key

    def _validate_mapping_items(self, mappings, template_rules, template_keys, seller_headers):
        seen_seller = set()
        seen_marketplace = set()
        for index, mapping in enumerate(mappings):
            seller_key, marketplace_key = self._validate_mapping_item(
                mapping,
                index,
                template_rules,
                template_keys,
                seller_headers,
                seen_seller,
                seen_marketplace,
            )
            seen_seller.add(seller_key)
            seen_marketplace.add(marketplace_key)
        return seen_marketplace

    def validate_mappings(self, mappings):
        template = self._marketplace_template
        seller_file = getattr(self, "seller_file", None) or self._seller_file
        if not template or not seller_file:
            return mappings

        self._validate_mappings_list(mappings)

        template_rules = template.template or {}
        template_keys = set(template_rules)
        seller_headers = set(seller_file.headers or [])

        seen_marketplace = self._validate_mapping_items(
            mappings,
            template_rules,
            template_keys,
            seller_headers,
        )

        missing_marketplace = template_keys - seen_marketplace
        if missing_marketplace:
            raise serializers.ValidationError("Mappings must include all marketplace template keys.")

        return mappings
