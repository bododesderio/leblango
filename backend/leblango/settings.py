import os
from pathlib import Path
from datetime import timedelta
from dotenv import load_dotenv

# ------------------------------------------------
# Base directory
# ------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent

# ------------------------------------------------
# Environment
# ------------------------------------------------
load_dotenv(BASE_DIR.parent / ".env")

# ------------------------------------------------
# Core Django settings
# ------------------------------------------------
# CRITICAL FIX #1: SECRET_KEY must be set (no default)
SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise ValueError("CRITICAL: SECRET_KEY environment variable must be set!")

# CRITICAL FIX #2: DEBUG defaults to False
DEBUG = os.getenv("DEBUG", "False") == "True"

# CRITICAL FIX #3: ALLOWED_HOSTS safer default
ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")

# ------------------------------------------------
# Installed Apps
# ------------------------------------------------
INSTALLED_APPS = [
    # Django
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.postgres",

    # Your apps
    "core.apps.CoreConfig",

    # Third-party
    "rest_framework",
    "rest_framework.authtoken",
    "drf_spectacular",
    "drf_spectacular_sidecar",
    "corsheaders",
]

# ------------------------------------------------
# Middleware
# ------------------------------------------------
MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# ------------------------------------------------
# CRITICAL FIX #4: CORS Configuration (environment-based)
# ------------------------------------------------
if DEBUG:
    CORS_ALLOW_ALL_ORIGINS = True
    print("⚠️  WARNING: CORS allowing all origins (DEBUG mode)")
else:
    CORS_ALLOWED_ORIGINS = os.getenv(
        "CORS_ALLOWED_ORIGINS",
        ""
    ).split(",")
    CORS_ALLOW_CREDENTIALS = True
    if not CORS_ALLOWED_ORIGINS or CORS_ALLOWED_ORIGINS == [""]:
        print("⚠️  WARNING: CORS_ALLOWED_ORIGINS not set in production!")

# ------------------------------------------------
# CRITICAL FIX #5: Production Security Headers
# ------------------------------------------------
if not DEBUG:
    # HTTPS/SSL
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'
    
    # HSTS (HTTP Strict Transport Security)
    SECURE_HSTS_SECONDS = 31536000  # 1 year
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    
    # Proxy settings (if behind nginx/load balancer)
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# ------------------------------------------------
# URL / WSGI
# ------------------------------------------------
ROOT_URLCONF = "leblango.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "core" / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "leblango.wsgi.application"

# ------------------------------------------------
# CRITICAL FIX #6: Database (No default password)
# ------------------------------------------------
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("DB_NAME", "leblango"),
        "USER": os.getenv("DB_USER", "leblango"),
        "PASSWORD": os.getenv("DB_PASSWORD"),  # NO DEFAULT!
        "HOST": os.getenv("DB_HOST", "127.0.0.1"),
        "PORT": os.getenv("DB_PORT", "5432"),
        "CONN_MAX_AGE": 600,  # Connection pooling
        "OPTIONS": {
            "connect_timeout": 10,
        },
    }
}

# Validate DB_PASSWORD is set
if not DATABASES["default"]["PASSWORD"]:
    raise ValueError("CRITICAL: DB_PASSWORD environment variable must be set!")

# ------------------------------------------------
# Redis Configuration
# ------------------------------------------------
REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = os.getenv("REDIS_PORT", "6379")
REDIS_DB = os.getenv("REDIS_DB", "0")
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", "")

if REDIS_PASSWORD:
    REDIS_URL = f"redis://:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}"
else:
    REDIS_URL = f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}"

# ------------------------------------------------
# Caching (Redis)
# ------------------------------------------------
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": REDIS_URL,
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "PASSWORD": REDIS_PASSWORD or None,
            "SOCKET_CONNECT_TIMEOUT": 5,
            "SOCKET_TIMEOUT": 5,
            "RETRY_ON_TIMEOUT": True,
        },
        "TIMEOUT": 60 * 60,  # 1 hour default
    }
}

# ------------------------------------------------
# Password Validation
# ------------------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
        "OPTIONS": {"min_length": 8},
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# ------------------------------------------------
# Internationalization
# ------------------------------------------------
LANGUAGE_CODE = "en-us"
TIME_ZONE = "Africa/Kampala"
USE_I18N = True
USE_TZ = True

# ------------------------------------------------
# Static & Media Files
# ------------------------------------------------
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR.parent / "staticfiles"

STATICFILES_DIRS = []
project_static = BASE_DIR.parent / "static"
if project_static.exists():
    STATICFILES_DIRS.append(project_static)

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR.parent / "media"

# ------------------------------------------------
# Logging Configuration
# ------------------------------------------------
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {message}",
            "style": "{",
        },
        "simple": {
            "format": "{levelname} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "level": "INFO",
            "class": "logging.StreamHandler",
            "formatter": "simple",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
    },
}

# ------------------------------------------------
# Defaults
# ------------------------------------------------
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ------------------------------------------------
# DRF & JWT
# ------------------------------------------------
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.AllowAny",
    ],
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.UserRateThrottle",
        "rest_framework.throttling.AnonRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {
        "user": "200/min",
        "anon": "50/min",
    },
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.LimitOffsetPagination",
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
    ] if not DEBUG else [
        "rest_framework.renderers.JSONRenderer",
        "rest_framework.renderers.BrowsableAPIRenderer",
    ],
    "EXCEPTION_HANDLER": "core.exceptions.custom_exception_handler",
    "PAGE_SIZE": 20,
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=60),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": True,  # SECURITY: Enable rotation
    "BLACKLIST_AFTER_ROTATION": True,  # SECURITY: Blacklist old tokens
    "UPDATE_LAST_LOGIN": True,
    
    "ALGORITHM": "HS256",
    "SIGNING_KEY": SECRET_KEY,
    "VERIFYING_KEY": None,
    
    "AUTH_HEADER_TYPES": ("Bearer",),
    "AUTH_HEADER_NAME": "HTTP_AUTHORIZATION",
    "USER_ID_FIELD": "id",
    "USER_ID_CLAIM": "user_id",
    
    "AUTH_TOKEN_CLASSES": ("rest_framework_simplejwt.tokens.AccessToken",),
    "TOKEN_TYPE_CLAIM": "token_type",
}

# ------------------------------------------------
# DRF Spectacular / OpenAPI
# ------------------------------------------------
SPECTACULAR_SETTINGS = {
    "TITLE": "Lëb Lango API",
    "DESCRIPTION": "Dictionary & Library API",
    "VERSION": "v1",
    "SERVE_INCLUDE_SCHEMA": False,
}

# ------------------------------------------------
# Feature Flags
# ------------------------------------------------
FUZZY_SEARCH_ENABLED = os.getenv("FUZZY_SEARCH_ENABLED", "true").lower() == "true"