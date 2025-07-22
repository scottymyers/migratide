# File: /home/ragequit/Migratide/Migratide/settings.py
from decouple import config
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
#LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/profile/'

# Security settings
SECRET_KEY = config('DJANGO_SECRET_KEY', default='jox$)wsaf$s7d&ts1%4@y@bv&%zcfvqr8hzhwgcb4!ox$$vq5v')
DEBUG = config('DJANGO_DEBUG', default=False, cast=bool)

ALLOWED_HOSTS = [
    'migrainetracker.coralbluelogic.com',
    '.pythonanywhere.com',
    'www.migratide.com',
    'migratide.com',
]

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_select2',
    'tracker',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # 'django.middleware.common.BrokenLinkEmailsMiddleware',
]

ROOT_URLCONF = 'Migratide.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
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

WSGI_APPLICATION = 'Migratide.wsgi.application'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

# Password validation
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
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# API Keys and Services
OPENWEATHERMAP_API_KEY = config('OPENWEATHERMAP_API_KEY', default='f555e075db9e374b16ab7d8d7b19d38e')
STRIPE_PUBLIC_KEY = config('STRIPE_PUBLIC_KEY', default='pk_test_51RnQSHP1TK6ovm5ttVjiWJpSrMNr29PiiTuMy1a1PqRRF4G8m27hZNb7L6GWwzK7nJDfN0Mup7qp5eBiOBouqJ0H00ovUnrmLR')
STRIPE_SECRET_KEY = config('STRIPE_SECRET_KEY', default='sk_test_51RnQSHP1TK6ovm5tQvmILAZys5lvCuW6OResq9H1C2qREWSmHtbpWepLuks1Wxn7zjjqL5PbhjQMTP3xwAr7Jb1c00Tu7gLh7v')
STRIPE_WEBHOOK_SECRET = config('STRIPE_WEBHOOK_SECRET', default='whsec_03br1JkAGSU2lmUjgTIGq6JJt0otIfsB')

# Logging configuration to reduce noise and handle errors
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'WARNING',
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'django.log'),
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'WARNING',
            'propagate': True,
        },
    },
}