from copy import copy

from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from core.constants import HEAD_DATA
from core.schema import PAGE_NUMBER_PARAMETER, PAGE_SIZE_PARAMETER
from core.serializers import ErrorResponseSerializer
from mapping.api.v1.paramters import MAPPING_ID_PARAMETER, MARKETPLACE_ID_PARAMETER, SELLER_ID_PARAMETER
from mapping.api.v1.schema_serializers import MappingCreateRequestSerializer, MappingsListResponseSerializer
from mapping.services.mapping_base import MappingService


class MappingsView(APIView):
    @extend_schema(
        operation_id="v1_mapping_list",
        parameters=[MARKETPLACE_ID_PARAMETER, SELLER_ID_PARAMETER, PAGE_NUMBER_PARAMETER, PAGE_SIZE_PARAMETER],
        responses={
            200: MappingsListResponseSerializer,
            400: ErrorResponseSerializer,
        },
    )
    def get(self, request: Request, *args, **kwargs):
        response = MappingService(request).list(request)
        return Response(response, status=response.get("code"), headers=HEAD_DATA)

    @extend_schema(
        request=MappingCreateRequestSerializer,
        responses={
            200: MappingsListResponseSerializer,
            412: ErrorResponseSerializer,
        },
    )
    def post(self, request: Request):
        response = MappingService(request).create(request)
        return Response(response, status=response.get("code"), headers=HEAD_DATA)

    def options(self, request: Request, *args, **kwargs):
        head_data = copy(HEAD_DATA)
        head_data["Access-Control-Allow-Methods"] = "GET, POST"
        return Response({}, status=status.HTTP_200_OK, headers=HEAD_DATA)


class MappingsDetailView(APIView):
    @extend_schema(
        operation_id="v1_mapping_retrieve",
        parameters=[MAPPING_ID_PARAMETER],
        responses={
            200: MappingsListResponseSerializer,
            404: ErrorResponseSerializer,
        },
    )
    def get(self, request: Request, *args, **kwargs):
        mapping_id = kwargs.get("mapping_id")
        response = MappingService(request).get(mapping_id)
        return Response(response, status=response.get("code"), headers=HEAD_DATA)

    def options(self, request: Request, *args, **kwargs):
        head_data = copy(HEAD_DATA)
        head_data["Access-Control-Allow-Methods"] = "GET"
        return Response({}, status=status.HTTP_200_OK, headers=HEAD_DATA)
