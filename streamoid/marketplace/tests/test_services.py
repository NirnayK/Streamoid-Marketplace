from unittest.mock import patch

import pytest
from rest_framework.parsers import JSONParser
from rest_framework.request import Request
from rest_framework.test import APIRequestFactory

from marketplace.models import Marketplace, MarketplaceTempate
from marketplace.serializers import MarketplaceTemplateListSerializer
from marketplace.services.marketplace_base import MarketplaceTemplateService

pytestmark = pytest.mark.django_db


@pytest.fixture
def api_rf():
    return APIRequestFactory()


@pytest.fixture
def marketplace():
    return Marketplace.objects.create(name="Demo Marketplace")


def build_request(api_rf, method="get", marketplace_id=None, data=None):
    path = "/"
    if marketplace_id is not None:
        path = f"/?marketplace_id={marketplace_id}"
    if method == "post":
        django_request = api_rf.post(path, data=data or {}, format="json")
        return Request(django_request, parsers=[JSONParser()])
    django_request = api_rf.get(path)
    return Request(django_request)


def test_list_requires_marketplace_id(api_rf):
    request = build_request(api_rf)
    service = MarketplaceTemplateService(request)

    response = service.list(request)

    assert response["code"] == 412
    assert response["errors"] == "No marketplace id found in request"


def test_list_returns_404_for_missing_marketplace(api_rf):
    request = build_request(api_rf, marketplace_id=999)
    service = MarketplaceTemplateService(request)

    response = service.list(request)

    assert response["code"] == 404
    assert response["errors"] == "Marketplace Not Found"


@patch("marketplace.services.marketplace_base.PaginationService.paginated_response", return_value={"ok": True})
def test_list_returns_paginated_response(paginated_response, api_rf, marketplace):
    MarketplaceTempate.objects.create(marketplace=marketplace, template={"sku": "1"})
    request = build_request(api_rf, marketplace_id=marketplace.id)
    service = MarketplaceTemplateService(request)
    service.marketplace = marketplace

    response = service.list(request)

    assert response == {"ok": True}
    args, _kwargs = paginated_response.call_args
    assert args[0].model is MarketplaceTempate
    assert args[1] is MarketplaceTemplateListSerializer


def test_get_returns_404_when_template_missing(api_rf, marketplace):
    request = build_request(api_rf, marketplace_id=marketplace.id)
    service = MarketplaceTemplateService(request)
    service.marketplace = marketplace

    response = service.get(marketplace_template_id=999)

    assert response["code"] == 404
    assert response["errors"] == "File Not Found"


@patch("marketplace.services.marketplace_base.PaginationService.paginated_response", return_value={"ok": True})
def test_get_returns_paginated_response(paginated_response, api_rf, marketplace):
    template = MarketplaceTempate.objects.create(marketplace=marketplace, template={"sku": "1"})
    request = build_request(api_rf, marketplace_id=marketplace.id)
    service = MarketplaceTemplateService(request)
    service.marketplace = marketplace

    response = service.get(marketplace_template_id=template.id)

    assert response == {"ok": True}
    args, _kwargs = paginated_response.call_args
    assert args[0].model is MarketplaceTempate
    assert args[1] is MarketplaceTemplateListSerializer


def test_post_returns_412_when_serializer_invalid(api_rf, marketplace):
    request = build_request(api_rf, method="post", marketplace_id=marketplace.id, data={"template": {}})
    service = MarketplaceTemplateService(request)
    service.marketplace = marketplace

    with patch("marketplace.services.marketplace_base.MarketplaceTemplateSerializer") as serializer_cls:
        serializer = serializer_cls.return_value
        serializer.is_valid.return_value = False
        serializer.errors = {"template": ["This field is required."]}
        response = service.create(request)

    assert response["code"] == 412
    assert response["errors"] == {"template": ["This field is required."]}


def test_post_returns_500_on_save_error(api_rf, marketplace):
    request = build_request(api_rf, method="post", marketplace_id=marketplace.id, data={"template": {"a": 1}})
    service = MarketplaceTemplateService(request)
    service.marketplace = marketplace

    with patch("marketplace.services.marketplace_base.MarketplaceTemplateSerializer") as serializer_cls:
        serializer = serializer_cls.return_value
        serializer.is_valid.return_value = True
        serializer.save.side_effect = Exception("boom")
        response = service.create(request)

    assert response["code"] == 500
    assert response["errors"] == "Faled to save the template. Please try again later"


def test_post_returns_paginated_response(api_rf, marketplace):
    request = build_request(api_rf, method="post", marketplace_id=marketplace.id, data={"template": {"a": 1}})
    service = MarketplaceTemplateService(request)
    service.marketplace = marketplace
    template = MarketplaceTempate.objects.create(marketplace=marketplace, template={"sku": "1"})

    with patch("marketplace.services.marketplace_base.MarketplaceTemplateSerializer") as serializer_cls:
        serializer = serializer_cls.return_value
        serializer.is_valid.return_value = True
        serializer.save.return_value = template
        with patch(
            "marketplace.services.marketplace_base.PaginationService.paginated_response", return_value={"ok": True}
        ) as paginated_response:
            response = service.create(request)

    assert response == {"ok": True}
    paginated_response.assert_called_once()
