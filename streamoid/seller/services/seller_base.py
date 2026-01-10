from rest_framework.request import Request

from streamoid.core.base_service import BaseService
from streamoid.seller.serializers import FileUploadSerialzier


class SellerBase(BaseService):
    def upload(self, request: Request):
        payload_file = request.FILES.get("file")
        serializer = FileUploadSerialzier(data={"payload_file": payload_file})
        if not serializer.is_valid():
            return self.get_412_response(errors=serializer.errors)
        
