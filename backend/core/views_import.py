# core/views_import.py

import csv
import io
import json

from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import DictionaryEntry, ImportJob, LibraryItem
from .permissions import IsStaffUser


class BaseImportView(APIView):
    permission_classes = [IsStaffUser]
    job_type = "dictionary"

    def create_job(self, request) -> ImportJob:
        return ImportJob.objects.create(
            job_type=self.job_type,
            created_by=request.user,
            created_at=timezone.now(),
            total_rows=0,
            success_rows=0,
            failed_rows=0,
            log="",
        )

    def finalize_job(self, job: ImportJob, log_lines):
        job.log = "\n".join(log_lines)
        job.save(
            update_fields=[
                "total_rows",
                "success_rows",
                "failed_rows",
                "log",
            ]
        )


class DictionaryImportCSVView(BaseImportView):
    """
    POST /api/admin/import/dictionary/csv
    Content-Type: multipart/form-data
    file: <csv>

    Expected headers (minimal):
    lemma,gloss_ll,gloss_en
    """

    def post(self, request):
        upload = request.FILES.get("file")
        if not upload:
            return Response(
                {"detail": "CSV file is required as 'file'."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        job = self.create_job(request)
        log = ["Starting dictionary CSV import."]

        try:
            data = upload.read().decode("utf-8-sig")
        except UnicodeDecodeError:
            return Response(
                {"detail": "Unable to decode CSV as UTF-8."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        reader = csv.DictReader(io.StringIO(data))

        for idx, row in enumerate(reader, start=1):
            job.total_rows += 1
            lemma = (row.get("lemma") or "").strip()
            if not lemma:
                job.failed_rows += 1
                log.append(f"Row {idx}: missing lemma.")
                continue

            entry, created = DictionaryEntry.objects.get_or_create(
                lemma=lemma,
                defaults={
                    "gloss_ll": row.get("gloss_ll") or "",
                    "gloss_en": row.get("gloss_en") or "",
                },
            )

            if not created:
                # update existing
                entry.gloss_ll = row.get("gloss_ll") or entry.gloss_ll
                entry.gloss_en = row.get("gloss_en") or entry.gloss_en
                entry.save()

            job.success_rows += 1

        self.finalize_job(job, log)

        return Response(
            {
                "detail": "Dictionary CSV import completed.",
                "job_id": job.id,
                "total_rows": job.total_rows,
                "success_rows": job.success_rows,
                "failed_rows": job.failed_rows,
            },
            status=status.HTTP_200_OK,
        )


class DictionaryImportJSONView(BaseImportView):
    """
    POST /api/admin/import/dictionary/json
    {
      "entries": [
        {"lemma": "...", "gloss_ll": "...", "gloss_en": "..."},
        ...
      ]
    }
    """

    def post(self, request):
        raw = request.data.get("entries")
        if raw is None and request.body:
            # allow raw JSON body
            try:
                parsed = json.loads(request.body.decode("utf-8"))
                raw = parsed.get("entries")
            except Exception:
                pass

        if not isinstance(raw, list):
            return Response(
                {"detail": "Expected 'entries' as a list."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        job = self.create_job(request)
        log = ["Starting dictionary JSON import."]

        for idx, item in enumerate(raw, start=1):
            job.total_rows += 1
            lemma = (item.get("lemma") or "").strip()
            if not lemma:
                job.failed_rows += 1
                log.append(f"Item {idx}: missing lemma.")
                continue

            entry, created = DictionaryEntry.objects.get_or_create(
                lemma=lemma,
                defaults={
                    "gloss_ll": item.get("gloss_ll") or "",
                    "gloss_en": item.get("gloss_en") or "",
                },
            )

            if not created:
                entry.gloss_ll = item.get("gloss_ll") or entry.gloss_ll
                entry.gloss_en = item.get("gloss_en") or entry.gloss_en
                entry.save()

            job.success_rows += 1

        self.finalize_job(job, log)

        return Response(
            {
                "detail": "Dictionary JSON import completed.",
                "job_id": job.id,
                "total_rows": job.total_rows,
                "success_rows": job.success_rows,
                "failed_rows": job.failed_rows,
            },
            status=status.HTTP_200_OK,
        )


class LibraryImportJSONView(BaseImportView):
    """
    POST /api/admin/import/library/json
    {
      "items": [
        {
          "title": "...",
          "description": "...",
          "url": "...",
          "item_type": "...",
          "is_published": true
        },
        ...
      ]
    }
    """
    job_type = "library"

    def post(self, request):
        raw = request.data.get("items")
        if raw is None and request.body:
            # allow raw JSON body
            try:
                parsed = json.loads(request.body.decode("utf-8"))
                raw = parsed.get("items")
            except Exception:
                pass

        if not isinstance(raw, list):
            return Response(
                {"detail": "Expected 'items' as a list."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        job = self.create_job(request)
        log = ["Starting library JSON import."]

        for idx, item in enumerate(raw, start=1):
            job.total_rows += 1
            title = (item.get("title") or "").strip()
            if not title:
                job.failed_rows += 1
                log.append(f"Item {idx}: missing title.")
                continue

            # Create or update library item
            library_item, created = LibraryItem.objects.get_or_create(
                title=title,
                defaults={
                    "description": item.get("description") or "",
                    "url": item.get("url") or "",
                    "item_type": item.get("item_type") or "",
                    "is_published": item.get("is_published", True),
                },
            )

            if not created:
                # update existing
                library_item.description = item.get("description") or library_item.description
                library_item.url = item.get("url") or library_item.url
                library_item.item_type = item.get("item_type") or library_item.item_type
                if "is_published" in item:
                    library_item.is_published = item.get("is_published")
                library_item.save()

            job.success_rows += 1
            log.append(f"Item {idx}: {'created' if created else 'updated'} '{title}'")

        self.finalize_job(job, log)

        return Response(
            {
                "detail": "Library JSON import completed.",
                "job_id": job.id,
                "total_rows": job.total_rows,
                "success_rows": job.success_rows,
                "failed_rows": job.failed_rows,
            },
            status=status.HTTP_200_OK,
        )