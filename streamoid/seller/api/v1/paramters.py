from drf_spectacular.utils import OpenApiParameter, OpenApiTypes

SELLER_ID_PARAMETER = OpenApiParameter(
    name="seller_id",
    type=OpenApiTypes.INT,
    location=OpenApiParameter.QUERY,
    required=True,
    description="ID of the seller that owns the files.",
)
FILE_ID_PARAMETER = OpenApiParameter(
    name="file_id",
    type=OpenApiTypes.INT,
    location=OpenApiParameter.PATH,
    required=True,
    description="ID of the seller file.",
)
