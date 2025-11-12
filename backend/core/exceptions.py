import logging
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import ValidationError as DjangoValidationError
from django.http import Http404
from django.db import IntegrityError

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    """
    Custom exception handler for DRF that provides consistent error responses
    and logs errors appropriately.
    """
    # Call REST framework's default exception handler first
    response = exception_handler(exc, context)

    # Get context details
    view = context.get('view', None)
    request = context.get('request', None)

    error_details = {
        'exception_type': type(exc).__name__,
        'exception_message': str(exc),
        'view': view.__class__.__name__ if view else 'Unknown',
        'path': request.path if request else 'Unknown',
        'method': request.method if request else 'Unknown',
    }

    # Handle DRF exceptions (response is already created)
    if response is not None:
        # Standardize the error response format
        if isinstance(response.data, dict):
            response.data['error_type'] = type(exc).__name__

        logger.warning(
            f"API Error: {error_details['exception_type']} - {error_details['exception_message']}",
            extra=error_details
        )
        return response

    # Handle Django's Http404
    if isinstance(exc, Http404):
        logger.info(f"404 Not Found: {error_details['path']}")
        return Response(
            {
                'detail': 'Not found.',
                'error_type': 'NotFound'
            },
            status=status.HTTP_404_NOT_FOUND
        )

    # Handle Django's ValidationError
    if isinstance(exc, DjangoValidationError):
        logger.warning(f"Validation Error: {str(exc)}", extra=error_details)
        return Response(
            {
                'detail': 'Validation error.',
                'errors': exc.message_dict if hasattr(exc, 'message_dict') else [str(exc)],
                'error_type': 'ValidationError'
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    # Handle database integrity errors
    if isinstance(exc, IntegrityError):
        logger.error(f"Database Integrity Error: {str(exc)}", extra=error_details)
        return Response(
            {
                'detail': 'Database integrity error. The operation violates a database constraint.',
                'error_type': 'IntegrityError'
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    # Handle any other unexpected exceptions
    logger.error(
        f"Unhandled Exception: {error_details['exception_type']} - {error_details['exception_message']}",
        extra=error_details,
        exc_info=True
    )

    return Response(
        {
            'detail': 'An unexpected error occurred. Please try again later.',
            'error_type': 'InternalServerError'
        },
        status=status.HTTP_500_INTERNAL_SERVER_ERROR
    )
