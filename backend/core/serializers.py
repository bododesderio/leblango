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


class LibraryItemSerializer(serializers.ModelSerializer):
    # Read-only label for category in responses (as requested)
    category = serializers.SlugRelatedField(read_only=True, slug_field="name")

    class Meta:
        model = LibraryItem
        fields = ("id", "title", "description", "category", "created_at")


# ------------ Auth / Accounts ------------ #

class SignUpSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)
    email = serializers.EmailField(required=False, allow_blank=True)

    class Meta:
        model = User
        fields = ("username", "email", "password")

    def validate_username(self, value: str):
        if User.objects.filter(username__iexact=value).exists():
            raise serializers.ValidationError(_("Username already taken."))
        return value

    def validate_email(self, value: str):
        # Only enforce uniqueness if provided
        if value and User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError(_("Email already in use."))
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
    # Accept category via slug on write; render as slug on read
    category = serializers.SlugRelatedField(
        queryset=LibraryCategory.objects.all(),
        slug_field="slug",
    )

    class Meta:
        model = LibrarySubmission
        fields = (
            "id",
            "title",
            "description",
            "category",
            "source_url",
            "status",
            "created_at",
        )
        read_only_fields = ("status", "created_at")


class LibraryEventSerializer(serializers.ModelSerializer):
    # Model choices on event_type already validate allowed values
    class Meta:
        model = LibraryEvent
        fields = ("id", "item", "event_type", "meta", "created_at")
        read_only_fields = ("created_at",)


class ImportJobSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImportJob
        fields = "__all__"
        read_only_fields = "__all__"
