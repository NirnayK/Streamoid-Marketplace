from pathlib import Path

from loguru import logger
from rest_framework.request import Request

from core.base_service import BaseService, PaginationService
from core.minio import MinioHandler
from seller.constants import CSV, SAMPLE_ROWS_COUNT
from seller.decorators.validation import validate_seller
from seller.file_parser import FileParser
from seller.models import Seller, SellerFiles
from seller.serializers import (
    FileUploadSerialzier,
    SellerCreateSerializer,
    SellerFilesSerializer,
    SellerSerializer,
)

log = logger.bind(component="seller_base")


class SellerHelperService:
    def __init__(self, seller: Seller):
        self.seller = seller
        self.minio = MinioHandler()

    def store_file(self, bucket_name, file, file_type):
        file_name = file.name
        is_stored = self.minio.store_file(bucket_name, file_name, file)
        if not is_stored:
            return None
        try:
            path = Path(bucket_name).joinpath(file_name)
            seller_file = SellerFiles.objects.create(
                seller=self.seller,
                name=file.name,
                file_type=file_type,
                path=str(path),
            )
            return seller_file
        except Exception as e:
            logger.error(f"Failed to store data in db | Error {str(e)}")
            if not self.minio.remove_file(bucket_name, file_name):
                logger.warning(
                    "Failed to cleanup MinIO file | bucket=%s object=%s",
                    bucket_name,
                    file_name,
                )
            return None


class SellerService(BaseService):
    def create(self, request: Request):
        serializer = SellerCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return self.get_412_response(errors=serializer.errors)
        try:
            seller = serializer.save()
        except Exception as e:
            logger.error(f"Failed to create seller | Error: {e}")
            return self.get_500_response(errors="Failed to create seller. Please try again later")
        return self.get_201_response(data=SellerSerializer(seller).data)

    def list(self, request: Request):
        query_params = request.query_params.dict()
        page_number, page_size = query_params.get("page_number"), query_params.get("page_size")
        sellers = Seller.objects.all().order_by("-created_at")
        return PaginationService(page_number, page_size).paginated_response(sellers, SellerSerializer)


class SellerFilesService(BaseService):
    def __init__(self, request: Request, *args, **kwargs):
        # Validate the seller
        self.seller_id = request.query_params.get("seller_id")
        self.seller = None
        if self.seller_id:
            self.seller = Seller.objects.filter(id=self.seller_id).last()

    @validate_seller
    def list(self, request: Request):
        query_params = request.query_params.dict()
        page_number, page_size = query_params.get("page_number"), query_params.get("page_size")
        files = SellerFiles.objects.filter(seller=self.seller).select_related("seller").order_by("-created_at")
        return PaginationService(page_number, page_size).paginated_response(files, SellerFilesSerializer)

    @validate_seller
    def get(self, file_id):
        file = SellerFiles.objects.filter(seller=self.seller, id=file_id).select_related("seller")
        if not file.exists():
            return self.get_404_response("File Not Found")
        return PaginationService().paginated_response(file, SellerFilesSerializer)

    @validate_seller
    def upload(self, request: Request):
        # Validate the file
        payload_file = request.FILES.get("file")
        serializer = FileUploadSerialzier(data={"payload_file": payload_file})
        if not serializer.is_valid():
            return self.get_412_response(errors=serializer.errors)
        file_type = serializer._file_type

        # Save the file in minio
        seller_file = SellerHelperService(self.seller).store_file(self.seller.bucket_name, payload_file, file_type)
        if not seller_file:
            return self.get_500_response(errors="Failed to store file. Please try again later")

        #  Parse the data
        headers, sample_rows, row_count = None, None, None
        if file_type == CSV:
            headers, sample_rows, row_count = FileParser.parse_csv(payload_file, SAMPLE_ROWS_COUNT)
        else:
            headers, sample_rows, row_count = FileParser.parse_excel(payload_file, SAMPLE_ROWS_COUNT)

        seller_file.rows_count = row_count
        seller_file.headers = headers
        seller_file.sample_rows = sample_rows
        seller_file.save(update_fields=["rows_count", "headers", "sample_rows", "updated_at"])

        return PaginationService().paginated_response(seller_file, SellerFilesSerializer)
