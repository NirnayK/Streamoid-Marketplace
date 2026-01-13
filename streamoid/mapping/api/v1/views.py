from copy import copy

from drf_spectacular.utils import OpenApiParameter, OpenApiTypes, extend_schema
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from core.constants import HEAD_DATA
from core.schema import PAGE_NUMBER_PARAMETER, PAGE_SIZE_PARAMETER
from core.serializers import ErrorResponseSerializer
from mapping.schema_serializers import MappingsListResponseSerializer
from mapping.serializers import MappingCreateSerializer
from mapping.services.mapping_base import MappingService

MARKETPLACE_ID_PARAMETER = OpenApiParameter(
    name="marketplace_id",
    type=OpenApiTypes.INT,
    location=OpenApiParameter.QUERY,
    description="Filter mappings by marketplace ID.",
)
SELLER_ID_PARAMETER = OpenApiParameter(
    name="seller_id",
    type=OpenApiTypes.INT,
    location=OpenApiParameter.QUERY,
    description="Filter mappings by seller ID.",
)
MAPPING_ID_PARAMETER = OpenApiParameter(
    name="mapping_id",
    type=OpenApiTypes.INT,
    location=OpenApiParameter.PATH,
    required=True,
    description="ID of the mapping.",
)


class MappingsView(APIView):
    @extend_schema(
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
        request=MappingCreateSerializer,
        responses={
            200: MappingsListResponseSerializer,
            412: ErrorResponseSerializer,
        },
    )
    def post(self, request: Request):
        response = MappingService(request).post(request)
        return Response(response, status=response.get("code"), headers=HEAD_DATA)

    def options(self, request: Request, *args, **kwargs):
        head_data = copy(HEAD_DATA)
        head_data["Access-Control-Allow-Methods"] = "GET, POST"
        return Response({}, status=status.HTTP_200_OK, headers=HEAD_DATA)


class MappingsDetailView(APIView):
    @extend_schema(
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
