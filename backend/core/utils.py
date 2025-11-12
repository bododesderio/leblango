"""
Utility functions for the core app
"""

import re
from typing import Optional
from django.utils.text import slugify as django_slugify


def generate_unique_slug(model_class, title: str, slug_field: str = 'slug') -> str:
    """
    Generate a unique slug for a model instance.

    Args:
        model_class: The Django model class
        title: The title to slugify
        slug_field: The name of the slug field (default: 'slug')

    Returns:
        A unique slug string
    """
    base_slug = django_slugify(title)
    slug = base_slug
    counter = 1

    while model_class.objects.filter(**{slug_field: slug}).exists():
        slug = f"{base_slug}-{counter}"
        counter += 1

    return slug


def sanitize_search_query(query: str) -> str:
    """
    Sanitize user search queries to prevent SQL injection or issues.

    Args:
        query: Raw search query string

    Returns:
        Sanitized query string
    """
    if not query:
        return ""

    # Remove potentially dangerous characters
    query = re.sub(r'[^\w\s\-]', '', query)

    # Limit length
    query = query[:200]

    # Remove extra whitespace
    query = ' '.join(query.split())

    return query.strip()


def get_client_ip(request) -> Optional[str]:
    """
    Get the client's IP address from the request.
    Handles proxy headers like X-Forwarded-For.

    Args:
        request: Django request object

    Returns:
        IP address string or None
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def format_file_size(bytes_size: int) -> str:
    """
    Convert bytes to human-readable file size.

    Args:
        bytes_size: File size in bytes

    Returns:
        Formatted string (e.g., "1.5 MB")
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_size < 1024.0:
            return f"{bytes_size:.1f} {unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.1f} PB"


def paginate_queryset(queryset, request, default_limit: int = 20):
    """
    Simple pagination helper for querysets.

    Args:
        queryset: Django queryset to paginate
        request: Django request object
        default_limit: Default number of items per page

    Returns:
        Tuple of (paginated_queryset, total_count, limit, offset)
    """
    try:
        limit = int(request.GET.get('limit', default_limit))
        limit = max(1, min(limit, 100))  # Between 1 and 100
    except (ValueError, TypeError):
        limit = default_limit

    try:
        offset = int(request.GET.get('offset', 0))
        offset = max(0, offset)
    except (ValueError, TypeError):
        offset = 0

    total_count = queryset.count()
    paginated = queryset[offset:offset + limit]

    return paginated, total_count, limit, offset