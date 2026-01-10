from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

head_data = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Credentials": "true",
    "Access-Control-Allow-Headers": "X-Requested-With, Content-Type, Set-Cookie",
    "content_type": "application/json",
}


class SellerPostView(APIView):
    def post(self, request: Request):
        pass

    def options(self, request, *args, **kwargs):
        head_data["Access-Control-Allow-Methods"] = "POST"
        return Response({}, status=status.HTTP_200_OK, headers=head_data)
