from io import BytesIO
from unittest.mock import patch

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from openpyxl import Workbook
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.request import Request
from rest_framework.test import APIRequestFactory

from seller.constants import CSV
from seller.models import Seller, SellerFiles
from seller.serializers import SellerFilesSerializer
from seller.services.seller_base import SellerBaseService, SellerHelperService

pytestmark = pytest.mark.django_db


@pytest.fixture
def api_rf():
    return APIRequestFactory()


@pytest.fixture
def seller():
    return Seller.objects.create(name="Demo Seller")


@pytest.fixture
def upload_csv():
    return SimpleUploadedFile("items.csv", b"sku,name\n1,Widget\n", content_type="text/csv")


@pytest.fixture
def upload_xlsx():
    workbook = Workbook()
    sheet = workbook.active
    sheet.append(["sku", "name"])
    sheet.append(["1", "Widget"])
    buffer = BytesIO()
    workbook.save(buffer)
    workbook.close()
    return SimpleUploadedFile(
        "items.xlsx",
        buffer.getvalue(),
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )


def build_request(api_rf, method="get", seller_id=None, upload=None):
    path = "/"
    if seller_id is not None:
        path = f"/?seller_id={seller_id}"
    if method == "post":
        django_request = api_rf.post(path, data={"file": upload}, format="multipart")
        return Request(django_request, parsers=[MultiPartParser(), FormParser()])
    django_request = api_rf.get(path)
    return Request(django_request)


@patch("seller.services.seller_base.minio_store_file", return_value=False)
def test_store_file_returns_none_when_minio_store_fails(_minio_store_file, seller, upload_csv):
    service = SellerHelperService(seller)
    result = service.store_file("bucket", upload_csv, CSV)

    assert result is None
    assert SellerFiles.objects.count() == 0


@patch("seller.services.seller_base.minio_remove_file", return_value=True)
@patch("seller.services.seller_base.SellerFiles.objects.create", side_effect=Exception("boom"))
@patch("seller.services.seller_base.minio_store_file", return_value=True)
def test_store_file_cleans_up_on_db_failure(
    _minio_store_file, _seller_create, minio_remove_file, seller, upload_csv
):
    service = SellerHelperService(seller)
    result = service.store_file("bucket", upload_csv, CSV)

    assert result is None
    minio_remove_file.assert_called_once_with("bucket", "items.csv")


@patch("seller.services.seller_base.minio_store_file", return_value=True)
def test_store_file_creates_seller_file(_minio_store_file, seller, upload_csv):
    service = SellerHelperService(seller)
    result = service.store_file("bucket", upload_csv, CSV)

    assert result is not None
    assert result.seller == seller
    assert result.name == "items.csv"
    assert result.type == CSV
    assert result.path == f"{seller.bucket_name}/file_name"
    assert SellerFiles.objects.count() == 1


def test_list_requires_seller_id(api_rf):
    request = build_request(api_rf)
    service = SellerBaseService(request)

    response = service.list(request)

    assert response["code"] == 412
    assert response["errors"] == "No seller id found in request"


def test_list_returns_404_for_missing_seller(api_rf):
    request = build_request(api_rf, seller_id=999)
    service = SellerBaseService(request)

    response = service.list(request)

    assert response["code"] == 404
    assert response["errors"] == "Seller Not Found"


@patch("seller.services.seller_base.PaginationService.paginated_response", return_value={"ok": True})
def test_list_returns_paginated_response(paginated_response, api_rf, seller):
    SellerFiles.objects.create(seller=seller, name="items.csv", type=CSV, path="bucket/items.csv")
    request = build_request(api_rf, seller_id=seller.id)
    service = SellerBaseService(request)

    response = service.list(request)

    assert response == {"ok": True}
    args, _kwargs = paginated_response.call_args
    assert args[0].model is SellerFiles
    assert args[1] is SellerFilesSerializer


def test_get_returns_404_when_file_missing(api_rf, seller):
    request = build_request(api_rf, seller_id=seller.id)
    service = SellerBaseService(request)

    response = service.get(file_id=999)

    assert response["code"] == 404
    assert response["errors"] == "File Not Found"


@patch("seller.services.seller_base.PaginationService.paginated_response", return_value={"ok": True})
def test_get_returns_paginated_response(paginated_response, api_rf, seller):
    seller_file = SellerFiles.objects.create(seller=seller, name="items.csv", type=CSV, path="bucket/items.csv")
    request = build_request(api_rf, seller_id=seller.id)
    service = SellerBaseService(request)

    response = service.get(file_id=seller_file.id)

    assert response == {"ok": True}
    args, _kwargs = paginated_response.call_args
    assert args[0].model is SellerFiles
    assert args[1] is SellerFilesSerializer


def test_upload_rejects_invalid_file(api_rf, seller):
    upload = SimpleUploadedFile("items.txt", b"nope", content_type="text/plain")
    request = build_request(api_rf, method="post", seller_id=seller.id, upload=upload)
    service = SellerBaseService(request)

    response = service.upload(request)

    assert response["code"] == 412
    assert "payload_file" in response["errors"]


@patch("seller.services.seller_base.SellerHelperService.store_file", return_value=None)
def test_upload_returns_500_when_storage_fails(_store_file, api_rf, seller, upload_csv):
    request = build_request(api_rf, method="post", seller_id=seller.id, upload=upload_csv)
    service = SellerBaseService(request)

    response = service.upload(request)

    assert response["code"] == 500
    assert response["errors"] == "Failed to store file. Please try again later"


@patch("seller.services.seller_base.PaginationService.set_response", return_value={"ok": True})
@patch("seller.services.seller_base.parse_csv", return_value=(["sku", "name"], [["1", "Widget"]], 1))
def test_upload_updates_rows_count_and_sets_metadata(_parse_csv, set_response, api_rf, seller, upload_csv):
    seller_file = SellerFiles.objects.create(seller=seller, name="items.csv", type=CSV, path="bucket/items.csv")
    request = build_request(api_rf, method="post", seller_id=seller.id, upload=upload_csv)
    service = SellerBaseService(request)

    with patch("seller.services.seller_base.SellerHelperService.store_file", return_value=seller_file):
        response = service.upload(request)

    seller_file.refresh_from_db()
    assert seller_file.rows_count == 1
    assert seller_file.headers == ["sku", "name"]
    assert seller_file.sample_rows == [["1", "Widget"]]
    assert response == {"ok": True}
    args, _kwargs = set_response.call_args
    assert args[0] == seller_file
    assert args[1] is SellerFilesSerializer


@patch("seller.services.seller_base.PaginationService.set_response", return_value={"ok": True})
@patch("seller.services.seller_base.parse_excel", return_value=(["sku", "name"], [["1", "Widget"]], 1))
def test_upload_uses_excel_parser(_parse_excel, set_response, api_rf, seller, upload_xlsx):
    seller_file = SellerFiles.objects.create(
        seller=seller, name="items.xlsx", type=".xlsx", path="bucket/items.xlsx"
    )
    request = build_request(api_rf, method="post", seller_id=seller.id, upload=upload_xlsx)
    service = SellerBaseService(request)

    with patch("seller.services.seller_base.SellerHelperService.store_file", return_value=seller_file):
        response = service.upload(request)

    assert response == {"ok": True}
    _parse_excel.assert_called_once()
    args, _kwargs = set_response.call_args
    assert args[0] == seller_file
    assert args[1] is SellerFilesSerializer
