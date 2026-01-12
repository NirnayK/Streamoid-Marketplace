from types import SimpleNamespace

from core.custom_validation import CustomValidatior


def _build_serializer(template):
    validator = CustomValidatior(template=SimpleNamespace(template=template))
    serializer_class = validator.build()
    assert serializer_class is not None
    return serializer_class


def test_custom_validator_validates_max_reference():
    template = {
        "mrp": {"type": "number", "min": 0, "required": True},
        "price": {"type": "number", "max": "$mrp", "required": True},
    }
    serializer_class = _build_serializer(template)

    serializer = serializer_class(data={"mrp": "100.00", "price": "99.99"})
    assert serializer.is_valid(), serializer.errors

    serializer = serializer_class(data={"mrp": "100.00", "price": "101.00"})
    assert not serializer.is_valid()
    assert "price" in serializer.errors


def test_custom_validator_validates_min_reference():
    template = {
        "floor": {"type": "number", "min": 0, "required": True},
        "discount": {"type": "number", "min": "$floor", "required": True},
    }
    serializer_class = _build_serializer(template)

    serializer = serializer_class(data={"floor": "10.00", "discount": "10.00"})
    assert serializer.is_valid(), serializer.errors

    serializer = serializer_class(data={"floor": "10.00", "discount": "9.99"})
    assert not serializer.is_valid()
    assert "discount" in serializer.errors
