from copy import copy

from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from streamoid.core.constants import HEAD_DATA
from streamoid.seller.services.seller_base import SellerBaseService


class SellerView(APIView):
    def get(self, request: Request, *args, **kwargs):
        response = SellerBaseService(request).list(request)
        return Response(response, status=response.get("code"), headers=HEAD_DATA)

    def post(self, request: Request, *args, **kwargs):
        response = SellerBaseService(request).upload(request)
        return Response(response, status=response.get("code"), headers=HEAD_DATA)

    def options(self, request: Request, *args, **kwargs):
        head_data = copy(HEAD_DATA)
        head_data["Access-Control-Allow-Methods"] = "GET, POST"
        return Response({}, status=status.HTTP_200_OK, headers=HEAD_DATA)


class SellerDetailView(APIView):
    def get(self, request: Request, *args, **kwargs):
        file_id = kwargs.get("file_id")
        response = SellerBaseService(request).get(file_id)
        return Response(response, status=response.get("code"), headers=HEAD_DATA)

    def options(self, request: Request, *args, **kwargs):
        head_data = copy(HEAD_DATA)
        head_data["Access-Control-Allow-Methods"] = "GET"
        return Response({}, status=status.HTTP_200_OK, headers=HEAD_DATA)
