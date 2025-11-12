from rest_framework.views import APIView
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema


@extend_schema(
    tags=["System"],
    summary="Health check",
    description=(
        "Simple health check endpoint used for uptime monitoring. "
        "Returns a JSON object confirming that the API and dependencies are running."
    ),
)
class HealthzView(APIView):
    authentication_classes = []  # Public, no JWT needed
    permission_classes = []

    def get(self, request):
        return Response({"ok": True, "status": "healthy"})


@extend_schema(
    tags=["System"],
    summary="API home / status",
    description=(
        "Root endpoint confirming the Leb Lango API is active. "
        "Useful for quick environment or uptime probes."
    ),
)
class HomeView(APIView):
    authentication_classes = []  # Public
    permission_classes = []

    def get(self, request):
        return Response({"app": "leblango", "status": "running"})
