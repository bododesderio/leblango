# core/views_dictionary.py

from django.db.models import Q, Value, FloatField
from django.contrib.postgres.search import TrigramSimilarity
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status

from .models import DictionaryEntry, SearchQueryLog


class PublicDictionarySearch(APIView):
    """
    Public dictionary search with fuzzy matching + analytics logging.

    GET /api/public/v1/dictionary/search?q=word&limit=20&offset=0&fuzzy=true
    
    Features:
    - Exact match priority
    - Fuzzy/typo tolerance using PostgreSQL trigrams
    - Configurable similarity threshold
    - Auto-suggest capability
    """
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        q = (request.GET.get("q") or "").strip()
        use_fuzzy = request.GET.get("fuzzy", "true").lower() == "true"
        
        # Get fuzzy search settings
        fuzzy_enabled = getattr(settings, 'FUZZY_SEARCH_ENABLED', True)
        similarity_threshold = float(request.GET.get("similarity", "0.3"))
        similarity_threshold = max(0.1, min(similarity_threshold, 1.0))  # Clamp 0.1-1.0

        qs = DictionaryEntry.objects.all()

        if q:
            if fuzzy_enabled and use_fuzzy:
                # FUZZY SEARCH: Use PostgreSQL trigram similarity
                qs = (
                    qs.annotate(
                        # Calculate similarity scores for each field
                        lemma_sim=TrigramSimilarity('lemma', q),
                        gloss_ll_sim=TrigramSimilarity('gloss_ll', q),
                        gloss_en_sim=TrigramSimilarity('gloss_en', q),
                    )
                    # Use the highest similarity score
                    .annotate(
                        max_similarity=Value(0.0, output_field=FloatField())
                    )
                    # Filter by threshold
                    .filter(
                        Q(lemma_sim__gt=similarity_threshold) |
                        Q(gloss_ll_sim__gt=similarity_threshold) |
                        Q(gloss_en_sim__gt=similarity_threshold)
                    )
                    # Order by best match first (prioritize lemma matches)
                    .order_by('-lemma_sim', '-gloss_ll_sim', '-gloss_en_sim')
                )
            else:
                # EXACT SEARCH: Basic substring matching (original behavior)
                qs = qs.filter(
                    Q(lemma__icontains=q)
                    | Q(gloss_ll__icontains=q)
                    | Q(gloss_en__icontains=q)
                ).order_by('lemma')

        else:
            # No query - return all ordered by lemma
            qs = qs.order_by('lemma')

        # Pagination
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

        # Get total count before slicing
        total_count = qs.count()
        
        # Slice results
        sliced = qs[offset : offset + limit]

        # Build response
        results = []
        for e in sliced:
            result = {
                "id": e.id,
                "lemma": e.lemma,
                "gloss_ll": e.gloss_ll,
                "gloss_en": e.gloss_en,
            }
            
            # Include similarity scores if fuzzy search was used
            if fuzzy_enabled and use_fuzzy and q:
                result["similarity"] = {
                    "lemma": round(getattr(e, 'lemma_sim', 0.0), 3),
                    "gloss_ll": round(getattr(e, 'gloss_ll_sim', 0.0), 3),
                    "gloss_en": round(getattr(e, 'gloss_en_sim', 0.0), 3),
                }
            
            results.append(result)

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
                "fuzzy_enabled": fuzzy_enabled and use_fuzzy,
                "similarity_threshold": similarity_threshold if (fuzzy_enabled and use_fuzzy) else None,
            },
        )

        return Response(
            {
                "count": total_count,
                "results": results,
                "search_type": "fuzzy" if (fuzzy_enabled and use_fuzzy and q) else "exact",
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


class PublicDictionaryAutocomplete(APIView):
    """
    Auto-suggest endpoint for dictionary search.
    
    GET /api/public/v1/dictionary/autocomplete?q=wor&limit=10
    
    Returns top matching lemmas for autocomplete/typeahead.
    """
    permission_classes = [permissions.AllowAny]
    
    def get(self, request):
        q = (request.GET.get("q") or "").strip()
        
        if not q or len(q) < 2:
            return Response(
                {"suggestions": []},
                status=status.HTTP_200_OK,
            )
        
        # Get limit
        try:
            limit = int(request.GET.get("limit", 10))
        except ValueError:
            limit = 10
        limit = max(1, min(limit, 50))
        
        # Use trigram similarity for fuzzy autocomplete
        suggestions = (
            DictionaryEntry.objects
            .annotate(similarity=TrigramSimilarity('lemma', q))
            .filter(similarity__gt=0.3)
            .order_by('-similarity')[:limit]
        )
        
        results = [
            {
                "lemma": entry.lemma,
                "gloss_en": entry.gloss_en[:50] if entry.gloss_en else "",  # Preview
                "similarity": round(entry.similarity, 3),
            }
            for entry in suggestions
        ]
        
        return Response(
            {"suggestions": results},
            status=status.HTTP_200_OK,
        )
