from copy import copy

from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from core.constants import HEAD_DATA
from core.schema import PAGE_NUMBER_PARAMETER, PAGE_SIZE_PARAMETER
from core.serializers import ErrorResponseSerializer
from marketplace.api.v1.parameters import MARKETPLACE_ID_PARAMETER, MARKETPLACE_TEMPLATE_ID_PARAMETER
from marketplace.api.v1.schema_serializers import (
    MarketplaceListResponseSerializer,
    MarketplaceResponseSerializer,
    MarketplaceTemplateCreateRequestSerializer,
    MarketplaceTemplateListResponseSerializer,
)
from marketplace.serializers import MarketplaceCreateSerializer
from marketplace.services.marketplace_base import MarketplaceService, MarketplaceTemplateService


class MarketplaceView(APIView):
    @extend_schema(
        operation_id="v1_marketplaces_list",
        parameters=[PAGE_NUMBER_PARAMETER, PAGE_SIZE_PARAMETER],
        responses={
            200: MarketplaceListResponseSerializer,
        },
    )
    def get(self, request: Request, *args, **kwargs):
        response = MarketplaceService().list(request)
        return Response(response, status=response.get("code"), headers=HEAD_DATA)

    @extend_schema(
        request=MarketplaceCreateSerializer,
        responses={
            201: MarketplaceResponseSerializer,
            412: ErrorResponseSerializer,
            500: ErrorResponseSerializer,
        },
    )
    def post(self, request: Request, *args, **kwargs):
        response = MarketplaceService().create(request)
        return Response(response, status=response.get("code"), headers=HEAD_DATA)

    def options(self, request: Request, *args, **kwargs):
        head_data = copy(HEAD_DATA)
        head_data["Access-Control-Allow-Methods"] = "GET, POST"
        return Response({}, status=status.HTTP_200_OK, headers=head_data)


class MarketplaceTemplateView(APIView):
    @extend_schema(
        operation_id="v1_marketplace_templates_list",
        parameters=[MARKETPLACE_ID_PARAMETER, PAGE_NUMBER_PARAMETER, PAGE_SIZE_PARAMETER],
        responses={
            200: MarketplaceTemplateListResponseSerializer,
            400: ErrorResponseSerializer,
            404: ErrorResponseSerializer,
            412: ErrorResponseSerializer,
        },
    )
    def get(self, request: Request, *args, **kwargs):
        response = MarketplaceTemplateService(request).list(request)
        return Response(response, status=response.get("code"), headers=HEAD_DATA)

    @extend_schema(
        request=MarketplaceTemplateCreateRequestSerializer,
        parameters=[MARKETPLACE_ID_PARAMETER],
        responses={
            200: MarketplaceTemplateListResponseSerializer,
            404: ErrorResponseSerializer,
            412: ErrorResponseSerializer,
            500: ErrorResponseSerializer,
        },
    )
    def post(self, request: Request, *args, **kwargs):
        response = MarketplaceTemplateService(request).create(request)
        return Response(response, status=response.get("code"), headers=HEAD_DATA)

    def options(self, request: Request, *args, **kwargs):
        head_data = copy(HEAD_DATA)
        head_data["Access-Control-Allow-Methods"] = "GET, POST"
        return Response({}, status=status.HTTP_200_OK, headers=HEAD_DATA)


class MarketplaceTemplateDetailView(APIView):
    @extend_schema(
        operation_id="v1_marketplace_templates_retrieve",
        parameters=[MARKETPLACE_ID_PARAMETER, MARKETPLACE_TEMPLATE_ID_PARAMETER],
        responses={
            200: MarketplaceTemplateListResponseSerializer,
            404: ErrorResponseSerializer,
            412: ErrorResponseSerializer,
        },
    )
    def get(self, request: Request, *args, **kwargs):
        marketplace_template_id = kwargs.get("marketplace_template_id")
        response = MarketplaceTemplateService(request).get(marketplace_template_id)
        return Response(response, status=response.get("code"), headers=HEAD_DATA)

    def options(self, request: Request, *args, **kwargs):
        head_data = copy(HEAD_DATA)
        head_data["Access-Control-Allow-Methods"] = "GET"
        return Response({}, status=status.HTTP_200_OK, headers=HEAD_DATA)
