from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from .models import (
    DictionaryEntry,
    EntryVariant,
    ImportJob,
    LibraryItem,
    LibrarySubmission,
    LibraryEvent,
    LibraryCategory,
)

User = get_user_model()


class EntryVariantSerializer(serializers.ModelSerializer):
    class Meta:
        model = EntryVariant
        fields = ("alias",)


class DictionaryEntrySerializer(serializers.ModelSerializer):
    variants = EntryVariantSerializer(many=True, read_only=True)

    class Meta:
        model = DictionaryEntry
        fields = (
            "id",
            "lemma",
            "gloss_ll",
            "gloss_en",
            "variants",
            "updated_at",
        )


class LibraryCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = LibraryCategory
        fields = ("id", "name", "slug")
        read_only_fields = ("slug",)


class LibraryItemSerializer(serializers.ModelSerializer):
    category = serializers.SlugRelatedField(
        read_only=True, 
        slug_field="name"
    )

    class Meta:
        model = LibraryItem
        fields = (
            "id", 
            "title", 
            "description", 
            "url",
            "category",
            "is_published",
            "created_at"
        )
        read_only_fields = ("created_at",)


# ------------ Auth / Accounts ------------ #

class SignUpSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True, 
        min_length=8,
        style={'input_type': 'password'}
    )
    email = serializers.EmailField(required=False, allow_blank=True)

    class Meta:
        model = User
        fields = ("username", "email", "password")

    def validate_username(self, value: str):
        if User.objects.filter(username__iexact=value).exists():
            raise serializers.ValidationError(_("Username already taken."))
        return value

    def validate_email(self, value: str):
        if value and User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError(_("Email already in use."))
        return value

    def validate_password(self, value: str):
        if len(value) < 8:
            raise serializers.ValidationError(_("Password must be at least 8 characters."))
        if value.isdigit():
            raise serializers.ValidationError(_("Password cannot be entirely numeric."))
        return value

    def create(self, validated_data):
        user = User(
            username=validated_data["username"],
            email=validated_data.get("email", ""),
        )
        user.set_password(validated_data["password"])
        user.save()
        return user


# ------------ Library Submissions / Events ------------ #

class LibrarySubmissionSerializer(serializers.ModelSerializer):
    """
    FIXED: Only use fields that actually exist in LibrarySubmission model
    Removed: category, source_url (these don't exist)
    """
    submitted_by = serializers.StringRelatedField(read_only=True)
    reviewed_by = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = LibrarySubmission
        fields = (
            "id",
            "title",
            "description",
            "url",  # FIXED: was 'source_url' 
            "status",
            "submitted_by",
            "reviewed_by",
            "reviewed_at",
            "rejection_reason",
            "created_at",
        )
        read_only_fields = (
            "status", 
            "submitted_by",
            "reviewed_by",
            "reviewed_at",
            "created_at"
        )


class LibraryEventSerializer(serializers.ModelSerializer):
    """
    FIXED: Removed 'meta' field that doesn't exist in model
    """
    user = serializers.StringRelatedField(read_only=True)
    item_title = serializers.CharField(source='item.title', read_only=True)

    class Meta:
        model = LibraryEvent
        fields = (
            "id", 
            "item", 
            "item_title",
            "event_type", 
            "user",
            "created_at"
        )
        read_only_fields = ("created_at", "user")


class ImportJobSerializer(serializers.ModelSerializer):
    created_by = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = ImportJob
        fields = (
            "id",
            "job_type",
            "created_by",
            "created_at",
            "total_rows",
            "success_rows",
            "failed_rows",
            "log",
        )
        read_only_fields = fields  # All fields are read-only