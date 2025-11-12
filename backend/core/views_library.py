from django.db.models import Q
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status

from .models import LibraryItem, LibrarySubmission, LibraryEvent
from .permissions import IsModeratorOrAdmin


class LibrarySearch(APIView):
    """
    Authenticated search over published library items.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        q = (request.GET.get("q") or "").strip()
        category = request.GET.get("category")

        # Only published items are visible
        qs = LibraryItem.objects.filter(is_published=True)

        if q:
            qs = qs.filter(
                Q(title__icontains=q) |
                Q(description__icontains=q)
            )

        if category:
            qs = qs.filter(category__slug=category)

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

        items = qs.order_by("-created_at")[offset: offset + limit]

        return Response(
            {
                "count": qs.count(),
                "results": [
                    {
                        "id": i.id,
                        "title": i.title,
                        "item_type": getattr(i, "item_type", None),
                        "category": i.category.name if getattr(i, "category", None) else None,
                    }
                    for i in items
                ],
            }
        )


class LibrarySubmit(APIView):
    """
    Allow an authenticated user to submit a library item suggestion.
    These go into LibrarySubmission for moderation.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        title = (request.data.get("title") or "").strip()
        if not title:
            return Response(
                {"detail": "Title is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        submission = LibrarySubmission.objects.create(
            submitted_by=request.user,
            title=title,
            description=request.data.get("description") or "",
            url=request.data.get("url") or "",
            # Optionally: wire category/item_type/file when frontend is ready.
        )

        return Response(
            {
                "id": submission.id,
                "status": submission.status,
                "detail": "Submission received and pending review.",
            },
            status=status.HTTP_201_CREATED,
        )


class LibraryTrack(APIView):
    """
    Track view/download/complete events for analytics.

    Expected JSON body:
    {
        "item_id": <int>,
        "event_type": "view" | "download" | "complete"
    }
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        item_id = request.data.get("item_id")
        event_type = request.data.get("event_type")

        if event_type not in ("view", "download", "complete"):
            return Response(
                {"detail": "Invalid event_type."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            item_id = int(item_id)
        except (TypeError, ValueError):
            return Response(
                {"detail": "item_id must be an integer."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            item = LibraryItem.objects.get(id=item_id, is_published=True)
        except LibraryItem.DoesNotExist:
            return Response(
                {"detail": "Item not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        LibraryEvent.objects.create(
            user=request.user,
            item=item,
            event_type=event_type,
        )

        return Response({"detail": "Tracked."}, status=status.HTTP_201_CREATED)


class LibrarySubmissionApprove(APIView):
    """
    Approve a library submission and create a published LibraryItem.
    POST /api/admin/library/submissions/<int:pk>/approve
    """
    permission_classes = [IsModeratorOrAdmin]

    def post(self, request, pk):
        try:
            submission = LibrarySubmission.objects.get(id=pk)
        except LibrarySubmission.DoesNotExist:
            return Response(
                {"detail": "Submission not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        if submission.status != "pending":
            return Response(
                {"detail": f"Submission is already {submission.status}."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Create the published library item
        library_item = LibraryItem.objects.create(
            title=submission.title,
            description=submission.description,
            url=submission.url,
            is_published=True,
            # Copy other fields as needed (category, item_type, file, etc.)
        )

        # Update submission status
        submission.status = "approved"
        submission.reviewed_by = request.user
        submission.save()

        return Response(
            {
                "detail": "Submission approved.",
                "submission_id": submission.id,
                "library_item_id": library_item.id,
            },
            status=status.HTTP_200_OK,
        )


class LibrarySubmissionReject(APIView):
    """
    Reject a library submission.
    POST /api/admin/library/submissions/<int:pk>/reject
    
    Optional JSON body:
    {
        "reason": "Explanation for rejection"
    }
    """
    permission_classes = [IsModeratorOrAdmin]

    def post(self, request, pk):
        try:
            submission = LibrarySubmission.objects.get(id=pk)
        except LibrarySubmission.DoesNotExist:
            return Response(
                {"detail": "Submission not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        if submission.status != "pending":
            return Response(
                {"detail": f"Submission is already {submission.status}."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Update submission status
        submission.status = "rejected"
        submission.reviewed_by = request.user
        
        # Optionally store rejection reason if your model has that field
        reason = request.data.get("reason", "")
        if reason and hasattr(submission, "rejection_reason"):
            submission.rejection_reason = reason
        
        submission.save()

        return Response(
            {
                "detail": "Submission rejected.",
                "submission_id": submission.id,
            },
            status=status.HTTP_200_OK,
        )
