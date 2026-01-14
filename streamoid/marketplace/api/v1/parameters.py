from drf_spectacular.utils import OpenApiParameter, OpenApiTypes

MARKETPLACE_ID_PARAMETER = OpenApiParameter(
    name="marketplace_id",
    type=OpenApiTypes.INT,
    location=OpenApiParameter.QUERY,
    required=True,
    description="ID of the marketplace that owns the templates.",
)
MARKETPLACE_TEMPLATE_ID_PARAMETER = OpenApiParameter(
    name="marketplace_template_id",
    type=OpenApiTypes.INT,
    location=OpenApiParameter.PATH,
    required=True,
    description="ID of the marketplace template.",
)
