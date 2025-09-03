"""
HTTP Production settings for AxeCollection project (for local testing).
This is a copy of production settings but with HTTP instead of HTTPS.
"""

import os
from pathlib import Path
from .settings import *

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

# Demo mode setting (from environment variable)
DEMO_MODE = os.environ.get("DEMO_MODE", "false").lower() == "true"

# SECURITY WARNING: keep the secret key used in production secret!
# SECRET_KEY is loaded from environment variable or separate file
SECRET_KEY = os.environ.get("SECRET_KEY")
if not SECRET_KEY:
    try:
        with open(BASE_DIR / "SECRET_KEY") as f:
            SECRET_KEY = f.read().strip()
    except FileNotFoundError:
        raise ValueError("SECRET_KEY must be set in environment or SECRET_KEY file")

# Production hosts - configurable via environment variables and database
# Format: comma-separated list of hosts, e.g. "localhost,127.0.0.1,example.com"
ALLOWED_HOSTS_ENV = os.environ.get("ALLOWED_HOSTS", "")

# Default hosts for backward compatibility
DEFAULT_ALLOWED_HOSTS = [
    "localhost",
    "127.0.0.1",
    "0.0.0.0",
    "django",  # For internal container communication
    "192.168.1.2",  # Your Unraid server IP
    "172.17.0.52",  # Docker internal IP
    # Production domain
    "yxor.pettersson-vik.se",
    "www.yxor.pettersson-vik.se",
]

# Start with default hosts
ALLOWED_HOSTS = DEFAULT_ALLOWED_HOSTS.copy()

# Add hosts from environment variable
if ALLOWED_HOSTS_ENV:
    env_hosts = [host.strip() for host in ALLOWED_HOSTS_ENV.split(",") if host.strip()]
    ALLOWED_HOSTS.extend(env_hosts)

# Add hosts from database (if available)
try:
    from axes.models import Settings

    settings_obj = Settings.get_settings()
    if settings_obj.external_hosts:
        db_hosts = [
            host.strip()
            for host in settings_obj.external_hosts.split(",")
            if host.strip()
        ]
        ALLOWED_HOSTS.extend(db_hosts)
        # Remove duplicates while preserving order
        seen = set()
        ALLOWED_HOSTS = [x for x in ALLOWED_HOSTS if not (x in seen or seen.add(x))]
except Exception:
    # If database is not available during startup, continue with current hosts
    pass

# Security settings for production
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# HTTPS settings - DISABLED for HTTP testing
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

# Database configuration for production SQLite
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "data" / "db.sqlite3",
        "OPTIONS": {
            "timeout": 20,  # 20 second timeout
            "check_same_thread": False,  # Allow multiple threads
        },
    }
}

# Static files configuration
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

# Media files configuration
# In production with Nginx, Django needs MEDIA_URL to generate correct URLs
# Nginx will handle the actual serving of files
MEDIA_URL = "/media/"  # Django needs this to generate correct URLs
MEDIA_ROOT = BASE_DIR / "media"

# Static files configuration (no WhiteNoise for now - will be handled by web server in production)
STATICFILES_STORAGE = "django.contrib.staticfiles.storage.StaticFilesStorage"

# Logging configuration - only console for Docker/Unraid
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {process:d} {thread:d} {message}",
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

# Cache configuration (optional, for better performance)
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "unique-snowflake",
    }
}

# Session configuration for production
SESSION_COOKIE_AGE = 30 * 24 * 60 * 60  # 30 days
SESSION_EXPIRE_AT_BROWSER_CLOSE = False
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SECURE = False  # HTTP allowed for testing

# CSRF configuration for HTTP testing
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SECURE = False  # HTTP allowed for testing

# CSRF trusted origins - configurable via environment variables and database
# Format: comma-separated list of origins, e.g. "http://example.com,http://localhost"
CSRF_TRUSTED_ORIGINS_ENV = os.environ.get("CSRF_TRUSTED_ORIGINS", "")

# Default origins for backward compatibility
DEFAULT_CSRF_TRUSTED_ORIGINS = [
    "http://localhost",
    "http://127.0.0.1",
    "http://0.0.0.0",
    "http://192.168.1.2",  # Your Unraid server IP
    "http://172.17.0.52",  # Docker internal IP
    # Production domain (both HTTP and HTTPS for testing)
    "http://yxor.pettersson-vik.se",
    "https://yxor.pettersson-vik.se",
    "http://www.yxor.pettersson-vik.se",
    "https://www.yxor.pettersson-vik.se",
]

# Start with default origins
CSRF_TRUSTED_ORIGINS = DEFAULT_CSRF_TRUSTED_ORIGINS.copy()

# Add origins from environment variable
if CSRF_TRUSTED_ORIGINS_ENV:
    env_origins = [
        origin.strip()
        for origin in CSRF_TRUSTED_ORIGINS_ENV.split(",")
        if origin.strip()
    ]
    CSRF_TRUSTED_ORIGINS.extend(env_origins)

# Add origins from database (if available)
try:
    from axes.models import Settings

    settings_obj = Settings.get_settings()
    if settings_obj.external_csrf_origins:
        db_origins = [
            origin.strip()
            for origin in settings_obj.external_csrf_origins.split(",")
            if origin.strip()
        ]
        CSRF_TRUSTED_ORIGINS.extend(db_origins)
        # Remove duplicates while preserving order
        seen = set()
        CSRF_TRUSTED_ORIGINS = [
            x for x in CSRF_TRUSTED_ORIGINS if not (x in seen or seen.add(x))
        ]
except Exception:
    # If database is not available during startup, continue with current origins
    pass

# Password validation (same as development)
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
        "OPTIONS": {
            "min_length": 12,
        },
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# Auth settings
LOGIN_URL = "/login/"
LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/"

# File upload settings for large backup files
DATA_UPLOAD_MAX_MEMORY_SIZE = 2 * 1024 * 1024 * 1024  # 2GB
FILE_UPLOAD_MAX_MEMORY_SIZE = 2 * 1024 * 1024 * 1024  # 2GB
# Dedikerad temporär katalog för filuppladdning
FILE_UPLOAD_TEMP_DIR = BASE_DIR / "tmp"
# Standardisera filrättigheter för uppladdningar
FILE_UPLOAD_PERMISSIONS = 0o644
FILE_UPLOAD_DIRECTORY_PERMISSIONS = 0o755

# Create necessary directories
os.makedirs(BASE_DIR / "data", exist_ok=True)
os.makedirs(BASE_DIR / "logs", exist_ok=True)
os.makedirs(BASE_DIR / "media", exist_ok=True)
os.makedirs(BASE_DIR / "staticfiles", exist_ok=True)
os.makedirs(BASE_DIR / "tmp", exist_ok=True)
