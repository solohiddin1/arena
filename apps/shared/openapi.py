"""Shared OpenAPI / Swagger helpers.

Defines the global ``Accept-Language`` header so every endpoint documents the
three supported languages (uz, ru, en) and returns localized content.
"""

from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter

# Supported response languages.
SUPPORTED_LANGUAGES = ["uz", "ru", "en"]
DEFAULT_LANGUAGE = "uz"

# Reusable parameter — drop into a specific view's ``@extend_schema`` when you
# want to document the header explicitly. It is also injected globally by the
# postprocessing hook below.
ACCEPT_LANGUAGE_PARAMETER = OpenApiParameter(
    name="Accept-Language",
    type=OpenApiTypes.STR,
    location=OpenApiParameter.HEADER,
    required=False,
    description="Response language. One of: uz, ru, en. Defaults to uz.",
    enum=SUPPORTED_LANGUAGES,
    default=DEFAULT_LANGUAGE,
)


def add_accept_language_parameter(result, generator, request, public):
    """Spectacular postprocessing hook: add the Accept-Language header globally.

    Adds the header to every operation that does not already declare it, so the
    Swagger UI exposes a language selector on all endpoints.
    """
    language_param = {
        "name": "Accept-Language",
        "in": "header",
        "required": False,
        "description": "Response language. One of: uz, ru, en. Defaults to uz.",
        "schema": {
            "type": "string",
            "enum": SUPPORTED_LANGUAGES,
            "default": DEFAULT_LANGUAGE,
        },
    }

    for path_item in result.get("paths", {}).values():
        for operation in path_item.values():
            if not isinstance(operation, dict):
                continue
            parameters = operation.setdefault("parameters", [])
            already_present = any(
                param.get("name") == "Accept-Language" and param.get("in") == "header"
                for param in parameters
            )
            if not already_present:
                parameters.append(language_param)

    return result