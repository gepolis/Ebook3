import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-51iz0mv4-(lh!8a#d_mz9_fmj7u75l9@f)9=upgc+8fpvk_yf('

DEBUG = True

LOGIN_URL = "/auth/"
LOGOUT_REDIRECT_URL = None
ALLOWED_HOSTS = ["*"]

AUTH_USER_MODEL = 'Accounts.Account'

SITE_ID = 1

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
]

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'Accounts',
    'MainApp',
    'PersonalArea',
    'crispy_forms',
    'crispy_bootstrap4',
    "django_extensions",
    'ckeditor',
    'storages',
    'channels',
    'ChatBot',
    'whitenoise.runserver_nostatic',
    'django_user_agents',
]


# Name of cache backend to cache user agents. If it not specified default
# cache alias will be used. Set to `None` to disable caching.
USER_AGENTS_CACHE = 'default'

MOS_RU_AUTH = True
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
'django_user_agents.middleware.UserAgentMiddleware',
]

ROOT_URLCONF = 'volunteer.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / "templates", BASE_DIR / "PersonalArea/templates/old"],
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

WSGI_APPLICATION = 'volunteer.wsgi.application'

ASGI_APPLICATION = 'volunteer.asgi.application'

DATABASES = {
    # 'default': {
    #    'ENGINE': 'django.db.backends.sqlite3',
    #    'NAME': BASE_DIR / 'db.sqlite3',
    # },

    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'default_db',
        'USER': 'gen_user',
        'PASSWORD': 'rokf4g6yp2',
        'HOST': '92.255.78.119',
        # 'PORT': '<db_port>',

    }
}

#

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

# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'ru-ru'

TIME_ZONE = 'Europe/Moscow'

USE_I18N = True

USE_TZ = True

# https://docs.djangoproject.com/en/4.2/howto/static-files/
STATIC_URL = 'static/'

# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

STATIC_URL = '/static/'

STATICFILES_DIRS = [
    BASE_DIR / "static"
]
STATIC_ROOT = BASE_DIR / "staticfiles"

MESSAGE_STORAGE = 'django.contrib.messages.storage.cookie.CookieStorage'

CRISPY_TEMPLATE_PACK = 'bootstrap4'

LOGIN_REDIRECT_URL = '/setup/'

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'

DEFAULT_FILE_STORAGE = 'volunteer.s3_storage.MediaStorage'

AWS_S3_ENDPOINT_URL = 'https://s3.timeweb.com'
AWS_S3_ACCESS_KEY_ID = "cm62321"
AWS_S3_SECRET_ACCESS_KEY = "afe65a4901c296608dc0d940dc1a58af"
AWS_QUERYSTRING_AUTH = False

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": 'channels.layers.InMemoryChannelLayer'
    }
}
ITEMS_FOR_PAGE = 25


REDIS_HOST = '0.0.0.0'
REDIS_PORT = 6379
CELERY_BROKER_URL = f'redis://{REDIS_HOST}:{REDIS_PORT}/0'
CELERY_BROKER_TRANSPORT_OPTIONS = {'visibility_timeout': 3600}
CELERY_RESULT_BACKEND = f'redis://{REDIS_HOST}:{REDIS_PORT}/0'
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.mail.ru'
EMAIL_PORT = 465
EMAIL_HOST_USER = 'ivanaksenov2010@mail.ru'
EMAIL_HOST_PASSWORD = 'SeZcYwzd9pxJX2As9niV'
EMAIL_USE_SSL = True
SERV = False