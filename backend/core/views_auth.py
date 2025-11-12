from rest_framework import status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.throttling import AnonRateThrottle
from django.contrib.auth import authenticate
from drf_spectacular.utils import extend_schema, OpenApiResponse

from .serializers import SignUpSerializer


class AuthRateThrottle(AnonRateThrottle):
    """
    Custom throttle for auth endpoints - more restrictive to prevent brute force
    5 attempts per minute per IP address
    """
    rate = '5/min'


@extend_schema(
    tags=["Authentication"],
    request=SignUpSerializer,
    responses={
        201: OpenApiResponse(description="User created successfully"),
        400: OpenApiResponse(description="Validation errors"),
        429: OpenApiResponse(description="Too many requests"),
    }
)
class SignUp(APIView):
    permission_classes = [permissions.AllowAny]
    throttle_classes = [AuthRateThrottle]  # ADDED: Rate limiting

    def post(self, request):
        """
        Create a new user account.

        Rate limited to 5 attempts per minute to prevent spam accounts.
        Returns an authentication token upon successful registration.
        """
        serializer = SignUpSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token, _ = Token.objects.get_or_create(user=user)
            return Response(
                {
                    "token": token.key,
                    "user": {
                        "id": user.id,
                        "username": user.username,
                        "email": user.email,
                    }
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )


@extend_schema(
    tags=["Authentication"],
    request={
        "application/json": {
            "type": "object",
            "properties": {
                "username": {"type": "string"},
                "password": {"type": "string", "format": "password"},
            },
            "required": ["username", "password"]
        }
    },
    responses={
        200: OpenApiResponse(description="Login successful"),
        400: OpenApiResponse(description="Invalid credentials"),
        403: OpenApiResponse(description="Account disabled"),
        429: OpenApiResponse(description="Too many login attempts"),
    }
)
class SignIn(APIView):
    permission_classes = [permissions.AllowAny]
    throttle_classes = [AuthRateThrottle]  # ADDED: Rate limiting

    def post(self, request):
        """
        Authenticate a user and return an auth token.

        Rate limited to 5 attempts per minute to prevent brute force attacks.
        """
        username = (request.data.get("username") or "").strip()
        password = (request.data.get("password") or "").strip()

        if not username or not password:
            return Response(
                {"detail": "Username and password are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = authenticate(username=username, password=password)
        if not user:
            return Response(
                {"detail": "Invalid credentials."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not user.is_active:
            return Response(
                {"detail": "Account is disabled."},
                status=status.HTTP_403_FORBIDDEN,
            )

        token, _ = Token.objects.get_or_create(user=user)
        return Response({
            "token": token.key,
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "is_staff": user.is_staff,
            }
        })
