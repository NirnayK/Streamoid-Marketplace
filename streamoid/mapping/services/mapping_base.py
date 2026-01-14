from loguru import logger
from rest_framework.request import Request

from core.base_service import BaseService, PaginationService
from mapping.models import Mappings
from mapping.serializers import MappingCreateSerializer, MappingsListSerializer


class MappingService(BaseService):
    def __init__(self, *args, **kwargs):
        self.mappings_select_related = [
            "marketplace_template",
            "marketplace_template__marketplace",
            "seller_file",
            "seller_file__seller",
        ]

    def list(self, request: Request):
        query_params = request.query_params.dict()
        page_number, page_size = query_params.get("page_number"), query_params.get("page_size")
        filters = {}
        if query_params.get("marketplace_id"):
            filters["marketplace_template__marketplace_id"] = query_params.get("marketplace_id")
        if query_params.get("seller_id"):
            filters["seller_file__seller_id"] = query_params.get("seller_id")

        mappings = (
            Mappings.objects.filter(**filters)
            .select_related(*self.mappings_select_related)
            .order_by("-created_at")
        )
        return PaginationService(page_number, page_size).paginated_response(mappings, MappingsListSerializer)

    def get(self, mapping_id):
        mapping = Mappings.objects.filter(id=mapping_id).select_related(*self.mappings_select_related)
        if not mapping.exists():
            return self.get_404_response("Mapping Not Found")
        return PaginationService().paginated_response(mapping, MappingsListSerializer)

    def create(self, request: Request):
        data = request.data
        serializer = MappingCreateSerializer(data=data)
        if not serializer.is_valid():
            return self.get_412_response(serializer.errors)
        try:
            mapping = serializer.save()
            return PaginationService().paginated_response(mapping, MappingsListSerializer)
        except Exception as e:
            logger.error(f"Failed to save mapping | Error: {e}")
            return self.get_500_response(errors="Failed to create mapping. Please try again later")
