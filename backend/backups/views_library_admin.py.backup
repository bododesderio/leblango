from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import LibrarySubmission, LibraryItem
from .permissions import IsManagerOrAdmin


class ApproveSubmission(APIView):
    permission_classes = [IsManagerOrAdmin]

    def post(self, request, pk):
        try:
            submission = LibrarySubmission.objects.get(pk=pk)
        except LibrarySubmission.DoesNotExist:
            return Response(
                {"detail": "Submission not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        if submission.status != LibrarySubmission.STATUS_PENDING:
            return Response(
                {"detail": "Submission already reviewed."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        item = LibraryItem.objects.create(
            title=submission.title,
            description=submission.description,
            url=submission.url,
            category=submission.category,
            is_published=True,
            submitted_by=submission.user,
            source_submission=submission,
        )

        submission.status = LibrarySubmission.STATUS_APPROVED
        submission.reviewed_by = request.user
        submission.reviewed_at = timezone.now()
        submission.rejection_reason = ""
        submission.save(update_fields=["status", "reviewed_by", "reviewed_at", "rejection_reason"])

        return Response(
            {"detail": "Submission approved.", "item_id": item.id},
            status=status.HTTP_200_OK,
        )


class RejectSubmission(APIView):
    permission_classes = [IsManagerOrAdmin]

    def post(self, request, pk):
        try:
            submission = LibrarySubmission.objects.get(pk=pk)
        except LibrarySubmission.DoesNotExist:
            return Response(
                {"detail": "Submission not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        if submission.status != LibrarySubmission.STATUS_PENDING:
            return Response(
                {"detail": "Submission already reviewed."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        reason = (request.data.get("reason") or "").strip()

        submission.status = LibrarySubmission.STATUS_REJECTED
        submission.reviewed_by = request.user
        submission.reviewed_at = timezone.now()
        submission.rejection_reason = reason
        submission.save(update_fields=["status", "reviewed_by", "reviewed_at", "rejection_reason"])

        return Response(
            {"detail": "Submission rejected."},
            status=status.HTTP_200_OK,
        )
