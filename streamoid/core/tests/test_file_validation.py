from types import SimpleNamespace

import pytest
from rest_framework import serializers

from core.file_validation import FileValidator, validate_file


def _build_template():
    return {
        "productName": {"type": "string", "maxLength": 150, "required": True},
        "brand": {"type": "string", "required": True},
        "gender": {"type": "enum", "choices": ["Men", "Women", "Boys", "Girls", "Unisex"], "required": True},
        "category": {
            "type": "enum",
            "choices": ["T-Shirts", "Jeans", "Dresses", "Sarees", "Shoes", "Bags", "Accessories"],
            "required": True,
        },
        "color": {"type": "string"},
        "size": {
            "type": "enum",
            "choices": ["XS", "S", "M", "L", "XL", "XXL", "32", "34", "36", "38", "40", "42"],
        },
        "mrp": {"type": "number", "min": 0, "required": True},
        "price": {"type": "number", "min": 0, "max": "$mrp", "required": True},
        "sku": {"type": "string", "unique": True, "required": True},
        "images": {"type": "array", "items": {"type": "url"}},
        "description": {"type": "string"},
        "material": {"type": "string"},
    }


def _build_mapping_data():
    mappings = [
        {"seller": "SKU", "marketplace": "sku"},
        {"seller": "Name", "marketplace": "productName"},
        {"seller": "BrandName", "marketplace": "brand"},
        {"seller": "Gender", "marketplace": "gender"},
        {"seller": "Category", "marketplace": "category"},
        {"seller": "Color", "marketplace": "color"},
        {"seller": "Size", "marketplace": "size"},
        {"seller": "MRP", "marketplace": "mrp"},
        {"seller": "Price", "marketplace": "price"},
        {"seller": "Material", "marketplace": "material"},
        {"seller": "Image1", "marketplace": "images"},
        {"seller": "Image2", "marketplace": "images"},
        {"seller": "Description", "marketplace": "description"},
    ]
    headers = [
        "SKU",
        "Name",
        "BrandName",
        "Gender",
        "Category",
        "Color",
        "Size",
        "MRP",
        "Price",
        "Material",
        "Image1",
        "Image2",
        "Quantity",
        "Description",
    ]
    rows = [
        [
            "SKU-1",
            "Cool T-Shirt",
            "Acme",
            "Men",
            "T-Shirts",
            "Blue",
            "M",
            "499.00",
            "399.00",
            "Cotton",
            "https://example.com/img1.jpg",
            "https://example.com/img2.jpg",
            "10",
            "Lol",
        ],
        [
            "SKU-2",
            "Relaxed Jeans",
            "DenimCo",
            "Women",
            "Jeans",
            "Black",
            "32",
            "1299.00",
            "999.00",
            "Denim",
            "https://example.com/img3.jpg",
            "",
            "5",
            "Lol",
        ],
    ]
    return mappings, headers, rows


def test_validate_file_maps_list_fields_and_validates():
    template = SimpleNamespace(template=_build_template())
    mappings, headers, rows = _build_mapping_data()

    validated = validate_file(template, mappings, headers, rows)

    assert validated[0]["sku"] == "SKU-1"
    assert validated[0]["productName"] == "Cool T-Shirt"
    assert validated[0]["images"] == ["https://example.com/img1.jpg", "https://example.com/img2.jpg"]
    assert validated[1]["images"] == ["https://example.com/img3.jpg"]


def test_file_validator_rejects_duplicate_unique_values():
    template = SimpleNamespace(template=_build_template())
    mappings, headers, _ = _build_mapping_data()
    rows = [
        [
            "SKU-1",
            "Cool T-Shirt",
            "Acme",
            "Men",
            "T-Shirts",
            "Blue",
            "M",
            "499.00",
            "399.00",
            "Cotton",
            "https://example.com/img1.jpg",
            "",
            "10",
            "Soft tee",
        ],
        [
            "SKU-1",
            "Relaxed Jeans",
            "DenimCo",
            "Women",
            "Jeans",
            "Black",
            "32",
            "1299.00",
            "999.00",
            "Denim",
            "https://example.com/img3.jpg",
            "",
            "5",
            "Relaxed fit",
        ],
    ]

    validator = FileValidator(template, mappings, headers, rows)
    with pytest.raises(serializers.ValidationError) as exc:
        validator.validate()

    assert exc.value.detail["field"] == "sku"
    assert "Duplicate value" in str(exc.value.detail["error"])


def test_file_validator_rejects_missing_required_fields():
    template = SimpleNamespace(template=_build_template())
    mappings, headers, _ = _build_mapping_data()
    rows = [
        [
            "SKU-1",
            "",
            "Acme",
            "Men",
            "T-Shirts",
            "Blue",
            "M",
            "499.00",
            "399.00",
            "Cotton",
            "https://example.com/img1.jpg",
            "",
            "10",
            "Soft tee",
        ]
    ]

    validator = FileValidator(template, mappings, headers, rows)
    with pytest.raises(serializers.ValidationError) as exc:
        validator.validate()

    assert int(exc.value.detail["row"]) == 0
    assert "productName" in exc.value.detail["errors"]


def test_file_validator_rejects_invalid_template():
    validator = FileValidator(SimpleNamespace(template=None), [], [], [])
    with pytest.raises(serializers.ValidationError) as exc:
        validator.validate()

    assert "Invalid template schema." in str(exc.value.detail)
