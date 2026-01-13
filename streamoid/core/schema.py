from drf_spectacular.utils import OpenApiParameter, OpenApiTypes

PAGE_NUMBER_PARAMETER = OpenApiParameter(
    name="page_number",
    type=OpenApiTypes.INT,
    location=OpenApiParameter.QUERY,
    description="Page number for pagination. Must be supplied with page_size.",
)
PAGE_SIZE_PARAMETER = OpenApiParameter(
    name="page_size",
    type=OpenApiTypes.INT,
    location=OpenApiParameter.QUERY,
    description="Page size for pagination. Must be supplied with page_number.",
)
