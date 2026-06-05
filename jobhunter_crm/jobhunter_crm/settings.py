"""Django settings for jobhunter_crm project."""

import os
import logging
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', 'django-insecure-dev-key-change-in-production')
DEBUG      = os.getenv('DJANGO_DEBUG', 'False').lower() in ('true', '1', 'yes')
ALLOWED_HOSTS = os.getenv('DJANGO_ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')
# Railway domenini avtomatik qo'shish
_railway_domain = os.getenv('RAILWAY_PUBLIC_DOMAIN')
if _railway_domain:
    ALLOWED_HOSTS.append(_railway_domain)
    CSRF_TRUSTED_ORIGINS = [f'https://{_railway_domain}']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_htmx',
    'django_apscheduler',
    'core',
    'dashboard',
    'vacancies',
    'companies',
    'platforms',
    'analytics',
    'parsers',
    'ai',
    'settings_app',
    'logs_app',
    'scheduler',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django_htmx.middleware.HtmxMiddleware',
]

ROOT_URLCONF = 'jobhunter_crm.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'core.context_processors.site_settings',
            ],
        },
    },
]

WSGI_APPLICATION = 'jobhunter_crm.wsgi.application'

# DB path — configurable so it can live on a persistent volume (Fly.io / Docker).
# DATABASE_PATH=/data/db.sqlite3 → SQLite stored on mounted volume.
DATABASE_PATH = os.getenv('DATABASE_PATH', str(BASE_DIR / 'db.sqlite3'))
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': DATABASE_PATH,
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'uz'
TIME_ZONE     = 'Asia/Tashkent'
USE_I18N      = True
USE_TZ        = True

STATIC_URL    = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT   = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL  = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ─── Groq AI ──────────────────────────────────────────────────────
GROQ_API_KEY              = os.getenv('GROQ_API_KEY', '')
GROQ_MODEL                = os.getenv('GROQ_MODEL', 'llama-3.1-8b-instant')
AI_COMPANY_CHECK_ENABLED  = os.getenv('AI_COMPANY_CHECK_ENABLED', 'True').lower() in ('true', '1', 'yes')
AI_DUPLICATE_CHECK_ENABLED = os.getenv('AI_DUPLICATE_CHECK_ENABLED', 'True').lower() in ('true', '1', 'yes')

# ─── Parser ───────────────────────────────────────────────────────
PARSER_INTERVAL   = int(os.getenv('PARSER_INTERVAL', '30'))
DAILY_TOTAL_LIMIT = int(os.getenv('DAILY_TOTAL_LIMIT', '200'))

# ─── Scoring ──────────────────────────────────────────────────────
SCORE_SALARY        = int(os.getenv('SCORE_SALARY', '20'))
SCORE_TOP_COMPANY   = int(os.getenv('SCORE_TOP_COMPANY', '30'))
SCORE_REMOTE        = int(os.getenv('SCORE_REMOTE', '20'))
SCORE_MIDDLE_SENIOR = int(os.getenv('SCORE_MIDDLE_SENIOR', '15'))
SCORE_FULL_DESCRIPTION = int(os.getenv('SCORE_FULL_DESCRIPTION', '10'))

# ─── APScheduler ──────────────────────────────────────────────────
APSCHEDULER_DATETIME_FORMAT = 'Y-m-d H:i:s'
SCHEDULER_CONFIG = {
    'apscheduler.jobstores.default': {
        'class': 'django_apscheduler.jobstores:DjangoJobStore',
    },
    'apscheduler.executors.default': {
        'class': 'apscheduler.executors.pool:ThreadPoolExecutor',
        'max_workers': 5,
    },
    'apscheduler.job_defaults.coalesce': True,
    'apscheduler.job_defaults.max_instances': 1,
}

# ─── Logging ──────────────────────────────────────────────────────
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '[{asctime}] {levelname} {name}: {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': LOG_LEVEL,
    },
    'loggers': {
        'django': {'handlers': ['console'], 'level': 'WARNING', 'propagate': False},
        'parsers': {'handlers': ['console'], 'level': LOG_LEVEL, 'propagate': False},
        'services': {'handlers': ['console'], 'level': LOG_LEVEL, 'propagate': False},
    },
}

# ─── Security (production) ────────────────────────────────────────
if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SESSION_COOKIE_SECURE   = True
    CSRF_COOKIE_SECURE      = True
