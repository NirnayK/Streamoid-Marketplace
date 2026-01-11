from copy import copy

from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from core.constants import HEAD_DATA
from mapping.services.mapping_base import MappingService


class MappingsView(APIView):
    def get(self, request: Request, *args, **kwargs):
        response = MappingService(request).list(request)
        return Response(response, status=response.get("code"), headers=HEAD_DATA)

    def post(self, request: Request):
        response = MappingService(request).post(request)
        return Response(response, status=response.get("code"), headers=HEAD_DATA)

    def options(self, request: Request, *args, **kwargs):
        head_data = copy(HEAD_DATA)
        head_data["Access-Control-Allow-Methods"] = "GET, POST"
        return Response({}, status=status.HTTP_200_OK, headers=HEAD_DATA)


class MappingsDetailView(APIView):
    def get(self, request: Request, *args, **kwargs):
        mapping_id = kwargs.get("mapping_id")
        response = MappingService(request).get(mapping_id)
        return Response(response, status=response.get("code"), headers=HEAD_DATA)

    def options(self, request: Request, *args, **kwargs):
        head_data = copy(HEAD_DATA)
        head_data["Access-Control-Allow-Methods"] = "GET"
        return Response({}, status=status.HTTP_200_OK, headers=HEAD_DATA)
