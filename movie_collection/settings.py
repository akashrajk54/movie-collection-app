"""
Django settings for movie_collection project.

Generated by 'django-admin startproject' using Django 4.2.6.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""

import os
from datetime import timedelta
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-u+mvnp5-z#8j%kpb@7if*o=efh^7=6c=t=pv1o8!bz&bythf92'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ["*"]

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": ("rest_framework.authentication.TokenAuthentication",),
    "DEFAULT_RENDERER_CLASSES": ("rest_framework.renderers.JSONRenderer",),
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.UserRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {
        "user": "100/hour",  # Please adjust
    },
}

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    "accounts_engine",
    "movies",
    "rest_framework_simplejwt",
    "rest_framework_simplejwt.token_blacklist",
    "rest_framework",
    "phonenumber_field",
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    "movie_collection.custom_middleware.TokenInvalidatedMiddleware",
]

ROOT_URLCONF = 'movie_collection.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'movie_collection.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / 'db.sqlite3',
#     }
# }

# DATABASES = {
#     "default": {
#         "ENGINE": "django.db.backends.postgresql",
#         "NAME": os.environ.get("POSTGRES_DB_NAME"),
#         "USER": os.environ.get("POSTGRES_USER"),
#         "PASSWORD": os.environ.get("POSTGRES_PASSWORD"),
#         "HOST": os.environ.get("POSTGRES_HOST"),
#         "PORT": os.environ.get("POSTGRES_PORT"),
#     }
# }

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "db_movie",
        "USER": "postgres",
        "PASSWORD": "Dedust!23",
        "HOST": "localhost",
        "PORT": "5432",
    }
}


# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=180),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "AUTH_HEADER_TYPES": ("Bearer",),
    "AUTH_TOKEN_CLASSES": ("rest_framework_simplejwt.tokens.AccessToken",),
}

# Logger
FORMATTERS = [
    {
        "verbose": {
            "format": "{levelname} TIME: {asctime:s} MODULE: {module} LINENO: {lineno:d} MESSAGE: {message}",
            "style": "{",
        },
        "simple": {
            "format": "{levelname} TIME: {asctime:s} MODULE: {module} LINENO: {lineno:d} MESSAGE: {message}",
            "style": "{",
        },
    },
]

HANDLERS = {
    "console_handler": {
        "class": "logging.StreamHandler",
        "formatter": "simple",
    },
    "error_handler": {
        "class": "logging.handlers.RotatingFileHandler",
        "filename": f"{BASE_DIR}/logs/log.log",
        "mode": "a",
        "encoding": "utf-8",
        "formatter": "simple",
        "backupCount": 5,
        "maxBytes": 1024 * 1024 * 5,
    },
    "info_handler": {
        "class": "logging.handlers.RotatingFileHandler",
        "filename": f"{BASE_DIR}/logs/log.log",
        "mode": "a",
        "formatter": "verbose",
        "backupCount": 5,
        "maxBytes": 1024 * 1024 * 5,
    },
}

LOGGERS = [
    {
        "info": {
            "handlers": ["console_handler", "info_handler"],
            "level": "DEBUG",
            "propagate": True,
        },
        "error": {
            "handlers": ["error_handler"],
            "level": "WARNING",
            "propagate": True,
        },
    },
]

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": FORMATTERS[0],
    "handlers": HANDLERS,
    "loggers": LOGGERS[0],
}

AUTH_USER_MODEL = "accounts_engine.CustomUser"

TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")
