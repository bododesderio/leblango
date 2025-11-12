from django.db import models
from django.conf import settings


# =========================
# Dictionary
# =========================

class DictionaryEntry(models.Model):
    lemma = models.CharField(max_length=255, unique=True)
    gloss_ll = models.TextField(blank=True)
    gloss_en = models.TextField(blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["lemma"]

    def __str__(self):
        return self.lemma


class EntryVariant(models.Model):
    entry = models.ForeignKey(
        DictionaryEntry,
        related_name="variants",
        on_delete=models.CASCADE,
    )
    alias = models.CharField(max_length=255)

    def __str__(self):
        return self.alias


# =========================
# Library Core
# =========================

class LibraryCategory(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class LibrarySubmission(models.Model):
    STATUS_PENDING = "pending"
    STATUS_APPROVED = "approved"
    STATUS_REJECTED = "rejected"

    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_APPROVED, "Approved"),
        (STATUS_REJECTED, "Rejected"),
    ]

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    url = models.URLField(blank=True)

    # This is the ONLY user FK we want:
    submitted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="library_submissions",
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING,
    )

    rejection_reason = models.TextField(blank=True)
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="reviewed_library_submissions",
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title


class LibraryItem(models.Model):
    category = models.ForeignKey(
        LibraryCategory,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="items",
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    url = models.URLField(blank=True)

    # Moderation / provenance
    is_published = models.BooleanField(default=False, db_index=True)
    submitted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="library_items_submitted",
    )
    source_submission = models.OneToOneField(
        LibrarySubmission,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="approved_item",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title


# =========================
# Library Events / Analytics
# =========================

class LibraryEvent(models.Model):
    EVENT_VIEW = "view"
    EVENT_DOWNLOAD = "download"
    EVENT_COMPLETE = "complete"

    EVENT_TYPES = (
        (EVENT_VIEW, "View"),
        (EVENT_DOWNLOAD, "Download"),
        (EVENT_COMPLETE, "Complete"),
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,            # allow anonymous / legacy rows
        blank=True,
        on_delete=models.SET_NULL,
        related_name="library_events",
    )
    item = models.ForeignKey(
        "core.LibraryItem",
        on_delete=models.CASCADE,
        related_name="events",
    )
    event_type = models.CharField(max_length=20, choices=EVENT_TYPES)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        who = self.user or "anonymous"
        return f"{who} {self.event_type} {self.item}"


# =========================
# Import Jobs
# =========================

class ImportJob(models.Model):
    job_type = models.CharField(max_length=50)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    total_rows = models.IntegerField(default=0)
    success_rows = models.IntegerField(default=0)
    failed_rows = models.IntegerField(default=0)
    log = models.TextField(blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.job_type} ({self.created_at})"


# =========================
# Search Query Logs
# =========================

class SearchQueryLog(models.Model):
    source = models.CharField(max_length=50)
    query = models.TextField()
    has_results = models.BooleanField(default=False)
    results_count = models.IntegerField(default=0)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    meta = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.source}: {self.query[:50]}"
