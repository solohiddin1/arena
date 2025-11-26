# core/swagger/parameters.py
from drf_spectacular.utils import OpenApiParameter, OpenApiTypes

ACCEPT_LANGUAGE_HEADER = [
    OpenApiParameter(
        name='Accept-Language',
        type=OpenApiTypes.STR,
        location=OpenApiParameter.HEADER,
        description='Language code (e.g. uz, ru, en)',
        required=False,
        default='uz'
    )
]
