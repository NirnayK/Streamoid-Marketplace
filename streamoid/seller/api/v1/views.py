from copy import copy

from drf_spectacular.utils import OpenApiParameter, OpenApiTypes, extend_schema
from rest_framework import status
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from core.constants import HEAD_DATA
from core.schema import PAGE_NUMBER_PARAMETER, PAGE_SIZE_PARAMETER
from core.serializers import ErrorResponseSerializer
from seller.schema_serializers import (
    SellerFileResponseSerializer,
    SellerFilesListResponseSerializer,
    SellerFileUploadRequestSerializer,
    SellerResponseSerializer,
)
from seller.serializers import (
    SellerCreateSerializer,
)
from seller.services.seller_base import SellerBaseService

SELLER_ID_PARAMETER = OpenApiParameter(
    name="seller_id",
    type=OpenApiTypes.INT,
    location=OpenApiParameter.QUERY,
    required=True,
    description="ID of the seller that owns the files.",
)
FILE_ID_PARAMETER = OpenApiParameter(
    name="file_id",
    type=OpenApiTypes.INT,
    location=OpenApiParameter.PATH,
    required=True,
    description="ID of the seller file.",
)


class SellerFilesView(APIView):
    # Required for multipart uploads and to surface the correct schema content type.
    parser_classes = (MultiPartParser, FormParser)

    @extend_schema(
        parameters=[SELLER_ID_PARAMETER, PAGE_NUMBER_PARAMETER, PAGE_SIZE_PARAMETER],
        responses={
            200: SellerFilesListResponseSerializer,
            400: ErrorResponseSerializer,
            404: ErrorResponseSerializer,
            412: ErrorResponseSerializer,
        },
    )
    def get(self, request: Request, *args, **kwargs):
        response = SellerBaseService(request).list(request)
        return Response(response, status=response.get("code"), headers=HEAD_DATA)

    @extend_schema(
        request=SellerFileUploadRequestSerializer,
        parameters=[SELLER_ID_PARAMETER],
        responses={
            200: SellerFileResponseSerializer,
            404: ErrorResponseSerializer,
            412: ErrorResponseSerializer,
            500: ErrorResponseSerializer,
        },
    )
    def post(self, request: Request, *args, **kwargs):
        response = SellerBaseService(request).upload(request)
        return Response(response, status=response.get("code"), headers=HEAD_DATA)

    def options(self, request: Request, *args, **kwargs):
        head_data = copy(HEAD_DATA)
        head_data["Access-Control-Allow-Methods"] = "GET, POST"
        return Response({}, status=status.HTTP_200_OK, headers=HEAD_DATA)


class SellerView(APIView):
    @extend_schema(
        request=SellerCreateSerializer,
        responses={
            201: SellerResponseSerializer,
            412: ErrorResponseSerializer,
            500: ErrorResponseSerializer,
        },
    )
    def post(self, request: Request, *args, **kwargs):
        response = SellerBaseService(request).create(request)
        return Response(response, status=response.get("code"), headers=HEAD_DATA)

    def options(self, request: Request, *args, **kwargs):
        head_data = copy(HEAD_DATA)
        head_data["Access-Control-Allow-Methods"] = "POST"
        return Response({}, status=status.HTTP_200_OK, headers=head_data)


class SellerFilesDetailView(APIView):
    @extend_schema(
        parameters=[SELLER_ID_PARAMETER, FILE_ID_PARAMETER],
        responses={
            200: SellerFilesListResponseSerializer,
            404: ErrorResponseSerializer,
            412: ErrorResponseSerializer,
        },
    )
    def get(self, request: Request, *args, **kwargs):
        file_id = kwargs.get("file_id")
        response = SellerBaseService(request).get(file_id)
        return Response(response, status=response.get("code"), headers=HEAD_DATA)

    def options(self, request: Request, *args, **kwargs):
        head_data = copy(HEAD_DATA)
        head_data["Access-Control-Allow-Methods"] = "GET"
        return Response({}, status=status.HTTP_200_OK, headers=HEAD_DATA)
