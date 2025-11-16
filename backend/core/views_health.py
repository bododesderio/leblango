# backend/core/views_health.py
# Enhanced health check with monitoring integration

from django.http import JsonResponse
from django.db import connection
from django.core.cache import cache
from django.conf import settings
import time


def healthz(request):
    """
    Basic health check endpoint for load balancers.
    Returns 200 OK if service is running.
    """
    return JsonResponse({"status": "healthy"}, status=200)


def health_detail(request):
    """
    Detailed health check with dependency status.
    Checks: Database, Redis, and application status.
    """
    start_time = time.time()
    health_status = {
        "status": "healthy",
        "timestamp": time.time(),
        "checks": {}
    }
    
    overall_healthy = True
    
    # Check database
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        health_status["checks"]["database"] = {
            "status": "healthy",
            "message": "PostgreSQL connected"
        }
    except Exception as e:
        health_status["checks"]["database"] = {
            "status": "unhealthy",
            "message": str(e)
        }
        overall_healthy = False
    
    # Check Redis cache
    try:
        cache.set("health_check", "ok", timeout=10)
        result = cache.get("health_check")
        if result == "ok":
            health_status["checks"]["cache"] = {
                "status": "healthy",
                "message": "Redis connected"
            }
        else:
            raise Exception("Cache verification failed")
    except Exception as e:
        health_status["checks"]["cache"] = {
            "status": "unhealthy",
            "message": str(e)
        }
        overall_healthy = False
    
    # Application status
    health_status["checks"]["application"] = {
        "status": "healthy",
        "debug_mode": settings.DEBUG,
        "environment": getattr(settings, 'SENTRY_ENVIRONMENT', 'unknown')
    }
    
    # Overall status
    health_status["status"] = "healthy" if overall_healthy else "unhealthy"
    health_status["response_time_ms"] = round((time.time() - start_time) * 1000, 2)
    
    status_code = 200 if overall_healthy else 503
    return JsonResponse(health_status, status=status_code)


def readiness(request):
    """
    Readiness probe for Kubernetes/container orchestration.
    Returns 200 when application is ready to serve traffic.
    """
    try:
        # Check database connectivity
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        
        # Check cache
        cache.set("readiness_check", "ready", timeout=5)
        
        return JsonResponse({
            "status": "ready",
            "timestamp": time.time()
        }, status=200)
    except Exception as e:
        return JsonResponse({
            "status": "not_ready",
            "error": str(e),
            "timestamp": time.time()
        }, status=503)


def liveness(request):
    """
    Liveness probe for Kubernetes/container orchestration.
    Returns 200 if application process is alive.
    """
    return JsonResponse({
        "status": "alive",
        "timestamp": time.time()
    }, status=200)
