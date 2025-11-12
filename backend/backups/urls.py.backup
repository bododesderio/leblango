from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

from . import views_dictionary
from . import views_library
from . import views_import
from . import views_analytics
from .views_auth import SignUp, SignIn
from .views_query_health import QueryHealthSummary


urlpatterns = [
    # ---------- Auth ----------
    # Full path: /api/auth/sign-up
    path("auth/sign-up", SignUp.as_view()),
    # Full path: /api/auth/sign-in  (optional legacy alongside JWT)
    path("auth/sign-in", SignIn.as_view()),

    # JWT endpoints (SimpleJWT)
    # /api/auth/jwt/create, /api/auth/jwt/refresh, /api/auth/jwt/verify
    path("auth/jwt/create", TokenObtainPairView.as_view()),
    path("auth/jwt/refresh", TokenRefreshView.as_view()),
    path("auth/jwt/verify", TokenVerifyView.as_view()),

    # Public dictionary API
    path(
        "api/public/v1/dictionary/search",
        views_dictionary.PublicDictionarySearch.as_view(),
        name="public-dictionary-search",
    ),
    path(
        "api/public/v1/dictionary/entry/<int:pk>",
        views_dictionary.PublicDictionaryEntryDetail.as_view(),
        name="public-dictionary-entry",
    ),

    # Library API
    path(
        "api/library/search",
        views_library.LibrarySearch.as_view(),
        name="library-search",
    ),
    path(
        "api/library/submit",
        views_library.LibrarySubmit.as_view(),
        name="library-submit",
    ),
    path(
        "api/library/track",
        views_library.LibraryTrack.as_view(),
        name="library-track",
    ),


    # Moderation actions
    path(
        "api/admin/library/submissions/<int:pk>/approve",
        views_library.LibrarySubmissionApprove.as_view(),
        name="library-submission-approve",
    ),
    path(
        "api/admin/library/submissions/<int:pk>/reject",
        views_library.LibrarySubmissionReject.as_view(),
        name="library-submission-reject",
    ),


    # Bulk importers
    path(
        "api/admin/import/dictionary/csv",
        views_import.DictionaryImportCSVView.as_view(),
        name="import-dictionary-csv",
    ),
    path(
        "api/admin/import/dictionary/json",
        views_import.DictionaryImportJSONView.as_view(),
        name="import-dictionary-json",
    ),
    path(
        "api/admin/import/library/json",
        views_import.LibraryImportJSONView.as_view(),
        name="import-library-json",
    ),

    # ---------- Query Health (admin) ----------
    # /api/admin/query-health/summary
    path(
        "admin/query-health/summary",
        QueryHealthSummary.as_view(),
    ),

    # Analytics
    path(
        "api/admin/query-health/summary",
        views_analytics.QueryHealthSummary.as_view(),
        name="query-health-summary",
    ),
    path(
        "api/admin/analytics/library/overview",
        views_analytics.LibraryAnalyticsOverview.as_view(),
        name="analytics-library-overview",
    ),
    path(
        "api/admin/analytics/dictionary/overview",
        views_analytics.DictionaryAnalyticsOverview.as_view(),
        name="analytics-dictionary-overview",
    ),
]
