from django.core.cache import cache
from datetime import timedelta
from django.utils import timezone
from django.db.models import Count
from rest_framework.views import APIView
from rest_framework.response import Response

from .models import SearchQueryLog
from .permissions import IsManagerOrAdmin


class QueryHealthSummary(APIView):
    """
    Admin-only summary of search health across dictionary & library.

    Shows:
    - total searches in window
    - no-result count + rate
    - top queries
    - top "no result" queries

    Cached briefly to support fast dashboards.
    """
    permission_classes = [IsManagerOrAdmin]

    def get(self, request):
        # Window length in days
        try:
            days = int(request.GET.get("days", 30) or 30)
        except ValueError:
            days = 30
        days = max(1, days)

        # Max rows for top lists
        try:
            limit = int(request.GET.get("limit", 50) or 50)
        except ValueError:
            limit = 50
        limit = max(1, min(limit, 200))

        cache_key = f"qh:summary:{days}:{limit}"
        cached = cache.get(cache_key)
        if cached is not None:
            return Response(cached)

        since = timezone.now() - timedelta(days=days)

        qs = SearchQueryLog.objects.filter(created_at__gte=since)

        total = qs.count()
        no_res = qs.filter(has_results=False).count()

        # Top no-result queries (these drive your backlog)
        top_missing = (
            qs.filter(has_results=False)
            .values("query", "source")
            .annotate(times=Count("id"))
            .order_by("-times")[:limit]
        )

        # Top queries overall
        top_queries = (
            qs.values("query", "source")
            .annotate(times=Count("id"))
            .order_by("-times")[:limit]
        )

        payload = {
            "window_days": days,
            "total_searches": total,
            "no_result_searches": no_res,
            "no_result_rate": (no_res / total) if total else 0.0,
            "top_no_result_queries": list(top_missing),
            "top_queries": list(top_queries),
        }

        # Cache for 60 seconds – responsive but fresh
        cache.set(cache_key, payload, timeout=60)

        return Response(payload)
