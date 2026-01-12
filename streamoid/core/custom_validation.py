import operator

from loguru import logger
from rest_framework import serializers

from core.helpers import ValidationHelpers
from marketplace.models import MarketplaceTempate

"""

{
  "productName": { "type": "string",  "maxLength": 150, "required": true},
  "brand":       { "type": "string", "required": true },
  "gender":      { "type": "enum", "choices": ["Men","Women","Boys","Girls","Unisex"] },
  "color":       { "type": "string" },
  "description": { "type": "string" },
  "material":    { "type": "string" },
  "mrp":   { "type": "number", "min": 0 ,"required": true},
  "price": { "type": "number", "min": 0, "max": "$mrp", "required": true },
  "images": {
    "type": "array",
    "items": { "type": "url" },
  },
  "sku": { "type": "string", "unique": true, "required": true }
}

"""


class CustomValidatior:
    """
    Generate a custom Django serializer from a marketplace template.
    The builder walks the template key/value rules and constructs serializer
    fields with validation cases based on the provided rules.
    """

    def __init__(self, *args, **kwargs):
        self.marketplace_template: MarketplaceTempate = kwargs.get("template")
        self.attrs = {}

    FIELD_TYPE_STRING = frozenset({"string", "str"})
    FIELD_TYPE_NUMBER = frozenset({"number", "float", "int", "integer"})
    FIELD_TYPE_ENUM = frozenset({"enum", "choice", "choices"})
    FIELD_TYPE_ARRAY = frozenset({"array", "list"})
    FIELD_TYPE_URL = frozenset({"url", "uri"})
    INTERNAL_VALUE_COMPARISON = "internal_args_comparison"
    VALIDATE_ARGS_FUNCTION = "validate_{arg_name}"

    FIELD_HANDLER_MAP = (
        (FIELD_TYPE_STRING, "handle_string"),
        (FIELD_TYPE_NUMBER, "handle_number"),
        (FIELD_TYPE_ENUM, "handle_enum"),
        (FIELD_TYPE_ARRAY, "handle_list"),
        (FIELD_TYPE_URL, "handle_url"),
    )

    def custom_validate_function_builder(self, function_type, **kwargs):
        if function_type == self.INTERNAL_VALUE_COMPARISON:
            arg_name = kwargs.get("arg_name")
            comparison_function = kwargs.get("comparison_function")
            compared_arg = kwargs.get("comparison_arg")
            raised_error = kwargs.get("raised_error") or f"{arg_name} failed validation."
            function_name = self.VALIDATE_ARGS_FUNCTION.format(arg_name=arg_name)

            def internal_comparison_validation(self, value):
                try:
                    compared_arg_raw = self.initial_data.get(compared_arg)
                    compared_field = self.fields.get(compared_arg)
                    compared_arg_value = compared_field.run_validation(compared_arg_raw)
                except serializers.ValidationError:
                    return value
                if not comparison_function(value, compared_arg_value):
                    raise serializers.ValidationError(raised_error)
                return value

            self.attrs[function_name] = internal_comparison_validation
            return

    def _extract_reference_field(self, value):
        if isinstance(value, str) and value.startswith("$") and len(value) > 1:
            return value[1:]
        return None

    def handle_string(self, name: str, rules: dict):
        required = rules.get("required")
        required = ValidationHelpers.evaluate_boolean(required, False)

        field = serializers.CharField(
            required=required,
            max_length=ValidationHelpers.get_variant_value(rules, "max", "length"),
            min_length=ValidationHelpers.get_variant_value(rules, "min", "length"),
            allow_blank=not required,
        )
        self.attrs[name] = field

    def handle_number(self, name: str, rules: dict):
        required = rules.get("required")
        required = ValidationHelpers.evaluate_boolean(required, False)

        min_value = ValidationHelpers.get_variant_value(rules, "min", "value")
        max_value = ValidationHelpers.get_variant_value(rules, "max", "value")
        min_reference = self._extract_reference_field(min_value)
        max_reference = self._extract_reference_field(max_value)
        if min_reference:
            self.custom_validate_function_builder(
                self.INTERNAL_VALUE_COMPARISON,
                arg_name=name,
                comparison_arg=min_reference,
                comparison_function=operator.ge,
                raised_error=f"{name} must be greater than or equal to {min_reference}.",
            )
            min_value = None

        if max_reference:
            self.custom_validate_function_builder(
                self.INTERNAL_VALUE_COMPARISON,
                arg_name=name,
                comparison_arg=max_reference,
                comparison_function=operator.le,
                raised_error=f"{name} must be less than or equal to {max_reference}.",
            )
            max_value = None

        max_digits = rules.get("max_digits") or rules.get("maxDigits") or 12
        decimal_places = rules.get("decimal_places") or rules.get("decimalPlaces") or 2

        field = serializers.DecimalField(
            required=required,
            allow_null=not required,
            min_value=min_value,
            max_value=max_value,
            max_digits=max_digits,
            decimal_places=decimal_places,
        )
        self.attrs[name] = field

    def handle_enum(self, name: str, rules: dict):
        required = rules.get("required")
        required = ValidationHelpers.evaluate_boolean(required, False)
        choices = rules.get("choices") or []
        field = serializers.ChoiceField(required=required, choices=choices)
        self.attrs[name] = field

    def handle_list(self, name: str, rules: dict):
        required = rules.get("required")
        required = ValidationHelpers.evaluate_boolean(required, False)
        items = rules.get("items") or {}
        child = self._build_list_child(items)
        field = serializers.ListField(
            required=required,
            allow_empty=not required,
            child=child,
        )
        self.attrs[name] = field

    def handle_url(self, name: str, rules: dict):
        required = rules.get("required")
        required = ValidationHelpers.evaluate_boolean(required, False)
        field = serializers.URLField(required=required, allow_null=not required)
        self.attrs[name] = field

    def generate_field(self, name: str, rules: dict):
        field_type = (rules.get("type") or "").lower()
        for field_types, handler_name in self.FIELD_HANDLER_MAP:
            if field_type in field_types:
                getattr(self, handler_name)(name, rules)

    def _build_list_child(self, rules: dict):
        field_type = (rules.get("type") or "").lower()
        if field_type in self.FIELD_TYPE_STRING:
            return serializers.CharField()
        if field_type in self.FIELD_TYPE_NUMBER:
            return serializers.DecimalField()
        if field_type in self.FIELD_TYPE_ENUM:
            return serializers.ChoiceField(choices=rules.get("choices") or [])
        if field_type in self.FIELD_TYPE_URL:
            return serializers.URLField()
        return serializers.JSONField()

    def build(self) -> serializers.Serializer:
        template = self.marketplace_template.template
        try:
            for name, rules in template.items():
                self.generate_field(name, rules)
            return type("CustomValidator", (serializers.Serializer,), self.attrs)
        except Exception as e:
            logger.warning(f"Failed to build custom validator | Error: {e}")
            return None
