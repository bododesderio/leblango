import os
from pathlib import Path
from datetime import timedelta
from dotenv import load_dotenv

# ------------------------------------------------
# Base directory
# ------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent  # /app/backend or your local backend path

# ------------------------------------------------
# Environment
# ------------------------------------------------
# .env is placed one level above backend/ (project root)
load_dotenv(BASE_DIR.parent / ".env")

# ------------------------------------------------
# Core Django settings
# ------------------------------------------------
SECRET_KEY = os.getenv("SECRET_KEY", "dev-change-me")
DEBUG = os.getenv("DEBUG", "True") == "True"

ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "*").split(",")

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

CORS_ALLOW_ALL_ORIGINS = True  # tighten in prod

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
# Database (PostgreSQL only)
# ------------------------------------------------
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("DB_NAME", "leblango"),
        "USER": os.getenv("DB_USER", "leblango"),
        "PASSWORD": os.getenv("DB_PASSWORD", "@dmin1234"),
        "HOST": os.getenv("DB_HOST", "127.0.0.1"),
        "PORT": os.getenv("DB_PORT", "5432"),
    }
}


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
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": REDIS_URL,
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "PASSWORD": REDIS_PASSWORD or None,
        },
        "TIMEOUT": 60 * 60,  # 1 hour default; adjust as needed
    }
}


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
# In Docker we mount:
#   static_files -> /app/staticfiles
#   media_files  -> /app/media
# Locally, BASE_DIR.parent is your project root.
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR.parent / "staticfiles"

STATICFILES_DIRS = []
project_static = BASE_DIR.parent / "static"
if project_static.exists():
    STATICFILES_DIRS.append(project_static)

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR.parent / "media"

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
    "EXCEPTION_HANDLER": "core.exceptions.custom_exception_handler",
    "PAGE_SIZE": 20,
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=60),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": False,
    "BLACKLIST_AFTER_ROTATION": False,
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
FUZZY_SEARCH_ENABLED = os.getenv("FUZZY_SEARCH_ENABLED", "true") == "true"
