# core/views_dictionary.py

from django.db.models import Q
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status

from .models import DictionaryEntry, SearchQueryLog


class PublicDictionarySearch(APIView):
    """
    Public dictionary search with basic pagination + analytics logging.

    GET /api/public/v1/dictionary/search?q=word&limit=20&offset=0
    """
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        q = (request.GET.get("q") or "").strip()

        qs = DictionaryEntry.objects.all()

        if q:
            qs = qs.filter(
                Q(lemma__icontains=q)
                | Q(gloss_ll__icontains=q)
                | Q(gloss_en__icontains=q)
            )

        # pagination
        try:
            limit = int(request.GET.get("limit", 20))
        except ValueError:
            limit = 20
        try:
            offset = int(request.GET.get("offset", 0))
        except ValueError:
            offset = 0

        limit = max(1, min(limit, 100))
        offset = max(0, offset)

        sliced = qs.order_by("lemma")[offset : offset + limit]

        results = [
            {
                "id": e.id,
                "lemma": e.lemma,
                "gloss_ll": e.gloss_ll,
                "gloss_en": e.gloss_en,
            }
            for e in sliced
        ]

        has_results = bool(results)

        # --- Analytics logging ---
        SearchQueryLog.objects.create(
            source="dictionary",
            query=q,
            has_results=has_results,
            results_count=len(results),
            user=request.user if request.user.is_authenticated else None,
            meta={
                "path": request.path,
                "ip": request.META.get("REMOTE_ADDR"),
            },
        )

        return Response(
            {
                "count": qs.count(),
                "results": results,
            },
            status=status.HTTP_200_OK,
        )


class PublicDictionaryEntryDetail(APIView):
    """
    Public single entry lookup.

    GET /api/public/v1/dictionary/entry/<id>
    """
    permission_classes = [permissions.AllowAny]

    def get(self, request, pk: int):
        try:
            entry = DictionaryEntry.objects.get(pk=pk)
        except DictionaryEntry.DoesNotExist:
            return Response(
                {"detail": "Entry not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response(
            {
                "id": entry.id,
                "lemma": entry.lemma,
                "gloss_ll": entry.gloss_ll,
                "gloss_en": entry.gloss_en,
            },
            status=status.HTTP_200_OK,
        )
