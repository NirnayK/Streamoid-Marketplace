from rest_framework import serializers

from core.custom_validation import CustomValidatior
from core.helpers import ValidationHelpers


class FileValidator:
    def __init__(self, marketplace_template, mappings, headers, rows):
        self.marketplace_template = marketplace_template
        self.mappings = mappings
        self.headers = headers
        self.rows = rows

    def _build_header_map(self):
        seller_to_marketplace = {}
        for mapping in self.mappings or []:
            if not isinstance(mapping, dict):
                continue
            seller_key = mapping.get("seller")
            marketplace_key = mapping.get("marketplace")
            if seller_key and marketplace_key:
                seller_to_marketplace[seller_key] = marketplace_key
        return [seller_to_marketplace.get(header) for header in (self.headers or [])]

    def _is_list_field(self, marketplace_key, template_rules):
        rules = template_rules.get(marketplace_key) or {}
        field_type = (rules.get("type") or "").lower()
        return field_type in CustomValidatior.FIELD_TYPE_ARRAY

    def _build_unique_sets(self, template_rules):
        unique_sets = {}
        for key, rules in template_rules.items():
            unique_value = ValidationHelpers.get_variant_value(rules, "unique", default=False)
            if ValidationHelpers.evaluate_boolean(unique_value, False):
                unique_sets[key] = set()
        return unique_sets

    def _map_row_values(self, header_map, row, template_rules):
        data = {}
        for index, marketplace_key in enumerate(header_map):
            if not marketplace_key:
                continue
            if index >= len(row):
                continue
            value = row[index]
            if self._is_list_field(marketplace_key, template_rules):
                if value in (None, ""):
                    continue
                data.setdefault(marketplace_key, []).append(value)
            else:
                data[marketplace_key] = value
        return data

    def _validate_unique_values(self, row_index, data, unique_sets):
        for key, seen in unique_sets.items():
            if key not in data:
                continue
            value = data[key]
            values = value if isinstance(value, list) else [value]
            for item in values:
                if item in seen:
                    raise serializers.ValidationError(
                        {"row": row_index, "field": key, "error": "Duplicate value for unique field."}
                    )
                seen.add(item)

    def validate(self):
        return list(self.iter_validated_rows())

    def iter_validated_rows(self):
        serializer_class = CustomValidatior(template=self.marketplace_template).build()
        if not serializer_class:
            raise serializers.ValidationError("Invalid template schema.")

        template_rules = self.marketplace_template.template or {}
        header_map = self._build_header_map()
        unique_sets = self._build_unique_sets(template_rules)

        for row_index, row in enumerate(self.rows):
            row_data = self._map_row_values(header_map, row, template_rules)
            serializer = serializer_class(data=row_data)
            if not serializer.is_valid():
                raise serializers.ValidationError({"row": row_index, "errors": serializer.errors})
            self._validate_unique_values(row_index, serializer.validated_data, unique_sets)
            yield serializer.validated_data


def validate_file(marketplace_template, mappings, headers, rows):
    return FileValidator(marketplace_template, mappings, headers, rows).validate()


def validate_file_iter(marketplace_template, mappings, headers, rows):
    return FileValidator(marketplace_template, mappings, headers, rows).iter_validated_rows()
