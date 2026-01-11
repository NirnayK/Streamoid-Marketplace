from rest_framework.request import Request

from core.base_service import BaseService, PaginationService
from mapping.models import Mappings
from mapping.serializers import MappingsListSerializer


class MappingService(BaseService):
    def list(self, request: Request):
        query_params = request.query_params.dict()
        page_number, page_size = query_params.get("page_number"), query_params.get("page_size")
        filters = {}
        if query_params.get("marketplace_id"):
            filters["marketplace_template__marketplace_id"] = query_params.get("marketplace_template_id")
        if query_params.get("seller_id"):
            filters["seller_file__seller_id"] = query_params.get("seller_id")

        mappings = (
            Mappings.objects.filter(**filters)
            .select_related(
                "marketplace_template", "marketplace_template__marketplace", "seller_file", "seller_file__seller"
            )
            .order_by("-created_at")
        )
        return PaginationService(page_number, page_size).paginated_response(mappings, MappingsListSerializer)

    def get(self, mapping_id):
        mapping = (
            Mappings.objects.filter(id=mapping_id)
            .select_related("marketplace_template", "marketplace_template__marketplace", "seller_file")
            .order_by("-created_at")
        )
        if not mapping.exists():
            return self.get_404_response("Mapping Not Found")
        return PaginationService().paginated_response(mapping, MappingsListSerializer)

    def post(self, request: Request):
        pass
