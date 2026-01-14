from drf_spectacular.utils import OpenApiParameter, OpenApiTypes

MARKETPLACE_ID_PARAMETER = OpenApiParameter(
    name="marketplace_id",
    type=OpenApiTypes.INT,
    location=OpenApiParameter.QUERY,
    description="Filter mappings by marketplace ID.",
)
SELLER_ID_PARAMETER = OpenApiParameter(
    name="seller_id",
    type=OpenApiTypes.INT,
    location=OpenApiParameter.QUERY,
    description="Filter mappings by seller ID.",
)
MAPPING_ID_PARAMETER = OpenApiParameter(
    name="mapping_id",
    type=OpenApiTypes.INT,
    location=OpenApiParameter.PATH,
    required=True,
    description="ID of the mapping.",
)
