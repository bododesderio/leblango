"""
URL Configuration for Leblango project.
"""
from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
)
from core.views_health import healthz, health_detail, readiness, liveness


urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),

    # Health checks
    path('healthz/', healthz, name='healthz'),
    path('health/', health_detail, name='health-detail'),
    path('readiness/', readiness, name='readiness'),
    path('liveness/', liveness, name='liveness'),

    # API
    path('api/', include('core.urls')),

    # OpenAPI Schema & Docs
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path(
        'api/docs/',
        SpectacularSwaggerView.as_view(url_name='schema'),
        name='swagger-ui'
    ),
]
