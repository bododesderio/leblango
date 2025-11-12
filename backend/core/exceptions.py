import logging

from django.core.exceptions import PermissionDenied
from django.http import Http404
from rest_framework.views import exception_handler as drf_exception_handler
from rest_framework.response import Response
from rest_framework import status

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    """
    Normalize all API errors to:

    {
        "success": False,
        "code": "validation_error|not_found|permission_denied|unauthenticated|server_error|...",
        "detail": "...",
        "errors": {...}  # when applicable
    }
    """

    response = drf_exception_handler(exc, context)

    if response is not None:
        raw = response.data

        # Normalize raw detail
        if isinstance(raw, str):
            detail = raw
            errors = None
        elif isinstance(raw, list):
            detail = raw
            errors = None
        elif isinstance(raw, dict):
            # if "detail" present, treat rest as errors; if not, treat dict as errors
            if "detail" in raw:
                detail = raw["detail"]
                errors = {k: v for k, v in raw.items() if k != "detail"} or None
            else:
                detail = "Validation error."
                errors = raw
        else:
            detail = str(raw)
            errors = None

        # Map to a code
        code = "error"

        if isinstance(exc, Http404):
            code = "not_found"
        elif isinstance(exc, PermissionDenied):
            code = "permission_denied"
        elif response.status_code == status.HTTP_400_BAD_REQUEST:
            code = "validation_error"
        elif response.status_code == status.HTTP_401_UNAUTHORIZED:
            code = "unauthenticated"
        elif response.status_code == status.HTTP_403_FORBIDDEN:
            code = "permission_denied"
        elif response.status_code == status.HTTP_404_NOT_FOUND:
            code = "not_found"
        elif 500 <= response.status_code < 600:
            code = "server_error"

        response.data = {
            "success": False,
            "code": code,
            "detail": detail,
        }
        if errors is not None:
            response.data["errors"] = errors

        return response

    # Non-DRF or unexpected: log + generic 500
    logger.exception("Unhandled API exception", exc_info=exc)

    return Response(
        {
            "success": False,
            "code": "server_error",
            "detail": "An unexpected error occurred. Please try again.",
        },
        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )
