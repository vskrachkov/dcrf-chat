from typing import Any, Dict, List

import dj_database_url
from environs import Env
from version import __version__

env = Env()
env.read_env()  # read .env file, if it exists

SECRET_KEY = env.str("SECRET_KEY")

DEBUG = env.bool("DEBUG", False)

ALLOWED_HOSTS = env.list("ALLOWED_HOSTS")

BASE_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

EXTERNAL_APPS = [
    "drf_spectacular",
    "corsheaders",
    "drf_health_check",
]

PROJECT_APPS: List[str] = ["chat"]

INSTALLED_APPS = BASE_APPS + EXTERNAL_APPS + PROJECT_APPS

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django_json_logging.middleware.AccessLogMiddleware",
    "corsheaders.middleware.CorsMiddleware",
]

ROOT_URLCONF = "urls"

AUTH_USER_MODEL = "chat.User"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
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

DATABASES = {
    "default": dj_database_url.parse(
        env.str("DATABASE_URL"),
        conn_max_age=env.int("DATABASE_CON_MAX_AGE", 60 * 60 * 24),
    )
}

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer"
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_L10N = True

USE_TZ = True

STATIC_URL = "/static/"

REST_FRAMEWORK = {
    "DEFAULT_RENDERER_CLASSES": ["rest_framework.renderers.JSONRenderer"],
    "DEFAULT_PARSER_CLASSES": ["rest_framework.parsers.JSONParser"],
    "DEFAULT_AUTHENTICATION_CLASSES": [],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated"
    ],
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}

AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
]

LOGIN_REDIRECT_URL = env.str("LOGIN_REDIRECT_URL", "/admin")

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "filters": {},
    "formatters": {
        "json": {"()": "django_json_logging.logging.JSONFormatter"},
    },
    "handlers": {
        "default": {
            "class": "logging.StreamHandler",
            "level": "INFO",
            "formatter": "json",
        },
    },
    "loggers": {
        "": {"handlers": ["default"], "level": "INFO", "propagate": True},
    },
}

STATIC_ROOT = env.str("STATIC_ROOT", "/tmp/static/")

DEFAULT_FILE_STORAGE = env.str(
    "DEFAULT_FILE_STORAGE", "storages.backends.s3boto3.S3Boto3Storage"
)
STATICFILES_STORAGE = env.str(
    "STATICFILES_STORAGE", "storages.backends.s3boto3.S3Boto3Storage"
)
AWS_S3_REGION_NAME = env.str("AWS_S3_REGION_NAME", "")
AWS_S3_ENDPOINT_URL = env.str("AWS_S3_ENDPOINT_URL", "")
AWS_ACCESS_KEY_ID = env.str("AWS_ACCESS_KEY_ID", "")
AWS_SECRET_ACCESS_KEY = env.str("AWS_SECRET_ACCESS_KEY", "")
AWS_STORAGE_BUCKET_NAME = env.str("AWS_STORAGE_BUCKET_NAME", "")
AWS_QUERYSTRING_EXPIRE = 3600 * 24
AWS_DEFAULT_ACL = env.str("AWS_DEFAULT_ACL", "public-read")
AWS_QUERYSTRING_AUTH = env.bool("AWS_QUERYSTRING_AUTH", False)

DBBACKUP_STORAGE = env.str(
    "DBBACKUP_STORAGE", "storages.backends.s3boto3.S3Boto3Storage"
)
DBBACKUP_STORAGE_OPTIONS = {
    "default_acl": "private",
    "access_key": env.str("DBBACKUP_ACCESS_KEY", ""),
    "secret_key": env.str("DBBACKUP_SECRET_ACCESS_KEY", ""),
    "bucket_name": env.str("DBBACKUP_BUCKET_NAME", ""),
    "endpoint_url": env.str("DBBACKUP_ENDPOINT_URL", ""),
    "location": env.str("DBBACKUP_PROJECT_NAME", None),
}
DBBACKUP_CLEANUP_KEEP = 7
DBBACKUP_FILENAME_TEMPLATE = (
    env.str("DBBACKUP_PROJECT_NAME", "dcrf-chat")
    + "-{datetime}.{extension}"
)

SPECTACULAR_SETTINGS: Dict[str, Any] = {
    "SERVE_PERMISSIONS": ["rest_framework.permissions.IsAuthenticated"],
    "SERVE_AUTHENTICATION": [
        "rest_framework.authentication.SessionAuthentication"
    ],
    "POSTPROCESSING_HOOKS": [
        "drf_spectacular_extensions.postprocessing_hooks.add_servers",
    ],
    "TITLE": "dcrf-chat API",
    "DESCRIPTION": """
## API Overview
dcrf-chat provides HTTP based API which you can use with simple HTTP client tools like [cURL](https://curl.se). 
We will use cURL in all following examples. 

## Date and time format
dcrf-chat API accepts `date` and `time` as string formatted according to `ISO 8601` [[wiki](https://en.wikipedia.org/wiki/ISO_8601)].
For example: 
``` 
2020-12-21
2020-12-21T15:22:22Z
2020-12-21T12:22:22-03
2020-12-21T17:22:22+02
```
    """,
    "VERSION": __version__,
}

DRF_INFO_ENDPOINT_PROJECT_NAME = "dcrf-chat"
DRF_INFO_ENDPOINT_VERSION = __version__

HEALTH_CHECK_PROVIDERS = {"drf_health_check.providers.DBHealthCheckProvider"}

if env.bool("USE_SENTRY", False) and env.str("SENTRY_DSN", ""):
    import sentry_sdk
    from sentry_sdk.integrations.django import DjangoIntegration

    sentry_sdk.init(
        dsn=env.str("SENTRY_DSN"),
        integrations=[DjangoIntegration()],
    )

DEFAULT_AUTO_FIELD = "django.db.models.AutoField"
