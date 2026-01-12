from marketplace.serializers import MarketplaceTemplateSerializer


def test_template_serializer_rejects_invalid_schema():
    serializer = MarketplaceTemplateSerializer(
        data={"marketplace_id": 1, "template": []},
    )

    assert not serializer.is_valid()
    assert serializer.errors["template"] == ["Invalid template schema"]
