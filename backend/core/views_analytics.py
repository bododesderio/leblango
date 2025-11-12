# core/views_analytics.py

from django.db.models import Count, Q
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import SearchQueryLog, LibraryEvent
from .permissions import IsStaffUser


class QueryHealthSummary(APIView):
    """
    GET /api/admin/query-health/summary

    High-level numbers for search quality.
    """
    permission_classes = [IsStaffUser]

    def get(self, request):
        total = SearchQueryLog.objects.count()
        no_results = SearchQueryLog.objects.filter(has_results=False).count()
        with_results = total - no_results

        top_missing = (
            SearchQueryLog.objects.filter(has_results=False)
            .values("query")
            .annotate(count=Count("id"))
            .order_by("-count")[:20]
        )

        return Response(
            {
                "total_queries": total,
                "with_results": with_results,
                "no_results": no_results,
                "no_results_rate": (no_results / total) if total else 0,
                "top_no_result_queries": list(top_missing),
            },
            status=status.HTTP_200_OK,
        )


class LibraryAnalyticsOverview(APIView):
    """
    GET /api/admin/analytics/library/overview

    Aggregate views/downloads/completions for all items.
    """
    permission_classes = [IsStaffUser]

    def get(self, request):
        agg = (
            LibraryEvent.objects.values("event_type")
            .annotate(count=Count("id"))
            .order_by()
        )
        by_type = {row["event_type"]: row["count"] for row in agg}

        return Response(
            {
                "total_events": sum(by_type.values()),
                "by_type": by_type,
            },
            status=status.HTTP_200_OK,
        )


class DictionaryAnalyticsOverview(APIView):
    """
    GET /api/admin/analytics/dictionary/overview
    """
    permission_classes = [IsStaffUser]

    def get(self, request):
        total = SearchQueryLog.objects.filter(source="dictionary").count()
        no_results = SearchQueryLog.objects.filter(
            source="dictionary", has_results=False
        ).count()
        with_results = total - no_results

        return Response(
            {
                "total_queries": total,
                "with_results": with_results,
                "no_results": no_results,
                "no_results_rate": (no_results / total) if total else 0,
            },
            status=status.HTTP_200_OK,
        )
