# core/utils/exceptions.py

from rest_framework.views import exception_handler


def custom_exception_handler(exc, context):
    """
    Wrap DRF + Django exceptions in a consistent JSON envelope.

    Response shape:
    {
        "success": false,
        "code": "<error_code>",
        "detail": "<human readable message>"
    }
    """
    response = exception_handler(exc, context)

    if response is None:
        # Non-DRF exceptions bubble up here if not caught.
        return None

    # Default code & message
    default_code = getattr(getattr(exc, "default_code", None), "__str__", lambda: None)()
    if not default_code:
        default_code = getattr(exc, "code", None) or "error"

    detail = response.data
    if isinstance(detail, dict) and "detail" in detail:
        message = detail["detail"]
    else:
        message = str(detail)

    response.data = {
        "success": False,
        "code": default_code,
        "detail": message,
    }
    return response
