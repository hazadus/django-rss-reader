"""
Django settings for RSS Reader project.

Generated by 'django-admin startproject' using Django 4.2.5.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""

from pathlib import Path

from django.urls import reverse_lazy
from environs import Env

env = Env()
env.read_env()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

SECRET_KEY = env.str("SECRET_KEY")
DEBUG = env.bool("DEBUG", False)

if SENTRY_DSN := env.str("SENTRY_DSN", None):  # noqa: C901
    import sentry_sdk

    def sentry_before_send(event: dict, hint: dict) -> dict | None:
        """
        Filters Sentry events before sending.

        This function filters out handled exceptions and logged errors.
        By doing this we will only receive unhandled exceptions on Sentry.

        :param dict event: The event dictionary containing exception data.
        :param dict hint: Additional information about the event, including
                the original exception.
        :return: The modified event dictionary, or None if the event should be
                ignored.
        """

        # Ignore logged errors
        if "logger" in event:
            return None

        # Ignore handled exceptions
        exceptions = event.get("exception", {}).get("values", [])
        if exceptions:
            exc = exceptions[-1]
            mechanism = exc.get("mechanism")

            if mechanism:
                if mechanism.get("handled"):
                    return None

        return event

    sentry_sdk.init(
        dsn=SENTRY_DSN,
        traces_sample_rate=0.5,
        before_send=sentry_before_send,
    )

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "filters": {"require_debug": {"()": "django.utils.log.RequireDebugTrue"}},
    "formatters": {
        "basic": {
            "format": "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
        "colored": {
            "()": "coloredlogs.ColoredFormatter",
            "format": "%(asctime)s %(levelname)s [%(name)s:%(lineno)s] %(message)s",
        },
    },
    "handlers": {
        "console_dev": {
            "class": "logging.StreamHandler",
            "formatter": "colored",
            "filters": ["require_debug"],
        },
        "django_file": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": "django_debug.log",
            "maxBytes": 1024 * 1024 * 10,
            "backupCount": 10,
            "formatter": "basic",
        },
        "server_file": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": "server_debug.log",
            "maxBytes": 1024 * 1024 * 10,
            "backupCount": 10,
            "formatter": "basic",
        },
    },
    "loggers": {
        "": {
            "handlers": ["console_dev", "django_file"],
            "level": "DEBUG" if DEBUG else "INFO",
        },
        "django.request": {
            "handlers": ["console_dev", "server_file"],
            "level": "INFO",
            "propagate": False,
        },
    },
}

ALLOWED_HOSTS = [
    "localhost",
    "127.0.0.1",
    "0.0.0.0",
    "176.53.161.145",
    "rss.hazadus.ru",
]

# Reference: https://docs.djangoproject.com/en/4.2/ref/settings/#csrf-trusted-origins
CSRF_TRUSTED_ORIGINS = [
    "http://rss.hazadus.ru",
    "https://rss.hazadus.ru",
]

if DEBUG:
    import socket

    hostname, _, ips = socket.gethostbyname_ex(socket.gethostname())
    INTERNAL_IPS = [ip[: ip.rfind(".")] + ".1" for ip in ips] + [
        "127.0.0.1",
        "10.0.2.2",
    ]


# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Third-party apps
    "debug_toolbar",
    "allauth",
    "allauth.account",
    # Local apps
    "users.apps.UsersConfig",
    "core.apps.CoreConfig",
    "feeds.apps.FeedsConfig",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "debug_toolbar.middleware.DebugToolbarMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    # django-allauth:
    "allauth.account.middleware.AccountMiddleware",
]

ROOT_URLCONF = "django_project.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
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

WSGI_APPLICATION = "django_project.wsgi.application"


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": env("DB_NAME"),
        "USER": env("DB_USER"),
        "PASSWORD": env("DB_PASSWORD"),
        "HOST": env("DB_HOST"),
        "PORT": env("DB_PORT"),
    }
}


# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

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


# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = "en-us"
TIME_ZONE = "Europe/Moscow"
USE_I18N = True
USE_TZ = True

# Media

MEDIA_URL = "/uploads/"
MEDIA_ROOT = BASE_DIR / "uploads"

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = "static/"
STATICFILES_DIRS = [
    BASE_DIR / "static",
]
STATIC_ROOT = BASE_DIR / "staticfiles"

STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        # WhiteNoise compression with caching
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}
WHITENOISE_MANIFEST_STRICT = False

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Authentication

AUTH_USER_MODEL = "users.CustomUser"
AUTHENTICATION_BACKENDS = [
    # Needed to login by username in Django admin, regardless of `allauth`
    "django.contrib.auth.backends.ModelBackend",
    # `allauth` specific authentication methods, such as login by email
    "allauth.account.auth_backends.AuthenticationBackend",
]

LOGIN_REDIRECT_URL = reverse_lazy("feeds:feed_list")
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_EMAIL_VERIFICATION = "none"
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_SIGNUP_PASSWORD_ENTER_TWICE = False
ACCOUNT_SESSION_REMEMBER = True
ACCOUNT_AUTHENTICATION_METHOD = "email"
ACCOUNT_UNIQUE_EMAIL = True
ACCOUNT_LOGOUT_ON_GET = True
ACCOUNT_SIGNUP_REDIRECT_URL = reverse_lazy("feeds:feed_list")
ACCOUNT_LOGOUT_REDIRECT_URL = reverse_lazy("account_login")

# Celery

CELERY_BROKER_URL = env("CELERY_BROKER_URL")
