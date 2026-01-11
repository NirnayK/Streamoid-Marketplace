from loguru import logger
from rest_framework.request import Request

from core.base_service import BaseService, PaginationService
from marketplace.decorators.validation import validate_marketplace
from marketplace.models import Marketplace, MarketplaceTempate
from marketplace.serializers import MarketplaceTemplateListSerializer, MarketplaceTemplateSerializer


class MarketplaceService(BaseService):
    def __init__(self, request: Request):
        # Validate the marketplace
        self.marketplace_id = request.query_params.get("marketplace_id")
        self.marketplace = None
        if self.marketplace:
            self.marketplace = Marketplace.objects.filter(id=self.seller_id).last()

    @validate_marketplace
    def list(self, request: Request):
        query_params = request.query_params.dict()
        page_number, page_size = query_params.get("page_number"), query_params.get("page_size")
        templates = (
            MarketplaceTempate.objects.filter(marketplace=self.marketplace)
            .select_related("marketplace")
            .order_by("-created_at")
        )
        return PaginationService(page_number, page_size).paginated_response(
            templates, MarketplaceTemplateListSerializer
        )

    @validate_marketplace
    def get(self, marketplace_template_id):
        template = MarketplaceTempate.objects.filter(
            marketplace=self.marketplace, id=marketplace_template_id
        ).select_related("marketplace")
        if not template.exists():
            return self.get_404_response("File Not Found")
        return PaginationService().paginated_response(template, MarketplaceTemplateListSerializer)

    @validate_marketplace
    def post(self, request: Request):
        data = request.data
        data["marketplace_id"] = self.marketplace_id
        serializer = MarketplaceTemplateSerializer(data=data)
        if not serializer.is_valid():
            return self.get_412_response(serializer.errors)
        try:
            template = serializer.save()
            return PaginationService().paginated_response(template, MarketplaceTemplateListSerializer)
        except Exception as e:
            logger.error(f"Failed to save template | Error: {e}")
            return self.get_500_response(errors="Faled to save the template. Please try again later")
