from rest_framework.serializers import FileField, Serializer

from core.constants import MAX_NAME_LENGTH
from core.serializers import BaseDetailResponseSerializer, BaseListResponseSerializer
from seller.serializers import SellerFilesSerializer, SellerSerializer


class SellerFileUploadRequestSerializer(Serializer):
    file = FileField(max_length=MAX_NAME_LENGTH)


class SellerResponseSerializer(BaseDetailResponseSerializer):
    data = SellerSerializer()


class SellerFilesListResponseSerializer(BaseListResponseSerializer):
    data = SellerFilesSerializer(many=True)


class SellerFileResponseSerializer(BaseDetailResponseSerializer):
    data = SellerFilesSerializer()
