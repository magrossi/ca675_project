"""
Django settings for web project.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""
import os

IS_PRODUCTION = os.environ.get('DJANGO_ENV') == 'production'

DEBUG = True
TEMPLATE_DEBUG = not IS_PRODUCTION

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

SECRET_KEY = os.environ['SECRET_KEY']

ALLOWED_HOSTS = []

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'widget_tweaks',
    'face_matcher',
    'django_seed',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

# Request object in template engin
TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'django.core.context_processors.static',
    'django.core.context_processors.tz',
    'django.contrib.messages.context_processors.messages',
    'django.core.context_processors.request',
)

ROOT_URLCONF = 'web.urls'

WSGI_APPLICATION = 'web.wsgi.application'

TEMPLATE_PATH = os.path.join(BASE_DIR, 'templates')
TEMPLATE_DIRS = (
    TEMPLATE_PATH,
)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': os.environ['DB_NAME'],
        'USER': os.environ['DB_USER'],
        'PASSWORD': os.environ['DB_PASS'],
        'HOST': os.environ['DB_SERVICE'],
        'PORT': os.environ['DB_PORT']
    }
}

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# after login homepage
LOGIN_REDIRECT_URL = '/matcher/'
LOGIN_URL='/login/'

MIN_PASSWORD_LENGTH = 3

STATIC_ROOT = os.path.join(BASE_DIR, 'static')
STATIC_URL = '/static/'

# STATICFILES_DIRS = (
#     STATIC_ROOT,
# )

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# redis
REDIS_HOST = 'redis'

# Celery settings
BROKER_URL = 'redis://' + REDIS_HOST
CELERY_RESULT_BACKEND = 'redis://' + REDIS_HOST
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'

# App settings
FACEREC_IMG_SIZE = (int(os.environ['FACEREC_WIDTH']), int(os.environ['FACEREC_HEIGHT']))
FACEREC_COMPONENTS = int(os.environ['FACEREC_COMPONENTS'])
FACEREC_MAX_SEED_IMG = 0 if os.getenv('FACEREC_MAX_SEED_IMG') is None else int(os.getenv('FACEREC_MAX_SEED_IMG'))

_IMG_BASE_DIR = os.getenv('IMG_BASE_DIR')
IMAGE_STORAGE_MODE = 'local' if _IMG_BASE_DIR else 's3'
IMAGE_STORAGE_LOCAL_DIR = _IMG_BASE_DIR
IMAGE_STORAGE_S3_ACCESS_KEY = os.getenv('IMG_BASE_S3_ACCESS_KEY')
IMAGE_STORAGE_S3_SECRET_KEY = os.getenv('IMG_BASE_S3_SECRET_KEY')
IMAGE_STORAGE_S3_BUCKET = os.getenv('IMG_BASE_S3_BUCKET')
IMAGE_STORAGE_S3_PREFIX = os.getenv('IMG_BASE_S3_PREFIX')
IMAGE_STORAGE_S3_REGION = os.getenv('IMG_BASE_S3_REGION')
