from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView
from core.views_health import HealthzView, HomeView

urlpatterns = [
    path("admin/", admin.site.urls),

    path("", HomeView.as_view(), name="home"),
    path("healthz/", HealthzView.as_view(), name="healthz"),
    path("api/healthz", HealthzView.as_view(), name="api-healthz"),
    path("api/health/", HealthzView.as_view(), name="api-health"),

    path("api/", include("core.urls")),

    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
]
