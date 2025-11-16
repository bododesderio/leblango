from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

from . import views_dictionary
from . import views_library
from . import views_library_admin
from . import views_import
from . import views_analytics
from .views_auth import SignUp, SignIn
from .views_query_health import QueryHealthSummary


urlpatterns = [
    # ---------- Auth ----------
    # Full path: /api/auth/sign-up
    path("auth/sign-up", SignUp.as_view(), name="auth-signup"),
    # Full path: /api/auth/sign-in  (optional legacy alongside JWT)
    path("auth/sign-in", SignIn.as_view(), name="auth-signin"),

    # JWT endpoints (SimpleJWT)
    # /api/auth/jwt/create, /api/auth/jwt/refresh, /api/auth/jwt/verify
    path("auth/jwt/create", TokenObtainPairView.as_view(), name="jwt-create"),
    path("auth/jwt/refresh", TokenRefreshView.as_view(), name="jwt-refresh"),
    path("auth/jwt/verify", TokenVerifyView.as_view(), name="jwt-verify"),

    # ---------- Public Dictionary API ----------
    path(
        "public/v1/dictionary/search",
        views_dictionary.PublicDictionarySearch.as_view(),
        name="public-dictionary-search",
    ),
    path(
        "public/v1/dictionary/entry/<int:pk>",
        views_dictionary.PublicDictionaryEntryDetail.as_view(),
        name="public-dictionary-entry",
    ),
    # NEW: Autocomplete endpoint
    path(
        "public/v1/dictionary/autocomplete",
        views_dictionary.PublicDictionaryAutocomplete.as_view(),
        name="public-dictionary-autocomplete",
    ),

    # ---------- Library API (Authenticated) ----------
    path(
        "library/search",
        views_library.LibrarySearch.as_view(),
        name="library-search",
    ),
    path(
        "library/submit",
        views_library.LibrarySubmit.as_view(),
        name="library-submit",
    ),
    path(
        "library/track",
        views_library.LibraryTrack.as_view(),
        name="library-track",
    ),

    # ---------- Admin: Library Moderation ----------
    path(
        "admin/library/submissions/<int:pk>/approve",
        views_library_admin.ApproveSubmission.as_view(),
        name="library-submission-approve",
    ),
    path(
        "admin/library/submissions/<int:pk>/reject",
        views_library_admin.RejectSubmission.as_view(),
        name="library-submission-reject",
    ),

    # ---------- Admin: Bulk Importers ----------
    path(
        "admin/import/dictionary/csv",
        views_import.DictionaryImportCSVView.as_view(),
        name="import-dictionary-csv",
    ),
    path(
        "admin/import/dictionary/json",
        views_import.DictionaryImportJSONView.as_view(),
        name="import-dictionary-json",
    ),
    path(
        "admin/import/library/json",
        views_import.LibraryImportJSONView.as_view(),
        name="import-library-json",
    ),

    # ---------- Admin: Query Health & Analytics ----------
    path(
        "admin/query-health/summary",
        QueryHealthSummary.as_view(),
        name="query-health-summary",
    ),
    path(
        "admin/analytics/library/overview",
        views_analytics.LibraryAnalyticsOverview.as_view(),
        name="analytics-library-overview",
    ),
    path(
        "admin/analytics/dictionary/overview",
        views_analytics.DictionaryAnalyticsOverview.as_view(),
        name="analytics-dictionary-overview",
    ),
]
