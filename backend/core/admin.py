# core/admin.py

from django.contrib import admin

from .models import (
    DictionaryEntry,
    EntryVariant,
    LibraryCategory,
    LibraryItem,
    LibrarySubmission,
    LibraryEvent,
    ImportJob,
    SearchQueryLog,
)


class EntryVariantInline(admin.TabularInline):
    model = EntryVariant
    extra = 1


@admin.register(DictionaryEntry)
class DictionaryEntryAdmin(admin.ModelAdmin):
    list_display = ("lemma", "updated_at")
    search_fields = ("lemma", "gloss_ll", "gloss_en", "variants__alias")
    inlines = [EntryVariantInline]


@admin.register(LibraryCategory)
class LibraryCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(LibraryItem)
class LibraryItemAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "category", "is_published", "created_at")
    list_filter = ("is_published", "category")
    search_fields = ("title", "description")


@admin.register(LibrarySubmission)
class LibrarySubmissionAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "submitted_by",
        "status",
        "created_at",
        "reviewed_by",
        "reviewed_at",
    )
    list_filter = ("status", "created_at")
    search_fields = ("title", "description", "submitted_by__username", "submitted_by__email")
    readonly_fields = ("submitted_by", "created_at", "reviewed_by", "reviewed_at")


@admin.register(LibraryEvent)
class LibraryEventAdmin(admin.ModelAdmin):
    list_display = ("item", "event_type", "user", "created_at")
    list_filter = ("event_type", "created_at")
    search_fields = ("item__title",)


@admin.register(ImportJob)
class ImportJobAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "job_type",
        "created_by",
        "created_at",
        "total_rows",
        "success_rows",
        "failed_rows",
    )
    readonly_fields = (
        "job_type",
        "created_by",
        "created_at",
        "total_rows",
        "success_rows",
        "failed_rows",
        "log",
    )
    ordering = ("-created_at",)


@admin.register(SearchQueryLog)
class SearchQueryLogAdmin(admin.ModelAdmin):
    list_display = (
        "source",
        "query",
        "has_results",
        "results_count",
        "user",
        "created_at",
    )
    list_filter = ("source", "has_results", "created_at")
    search_fields = ("query", "user__username", "user__email")
    readonly_fields = (
        "source",
        "query",
        "has_results",
        "results_count",
        "user",
        "created_at",
        "meta",
    )
    ordering = ("-created_at",)