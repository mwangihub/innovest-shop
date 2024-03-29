import environ
from user.auth_config import *

env = environ.Env(
    DEBUG=(bool, True),
    DEV_MODE=(bool, False)
)

BASE_DIR = Path(__file__).resolve().parent.parent
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))
SECRET_KEY = env("SECRET_KEY")
DEBUG = env('DEBUG')

DEV_MODE = env('DEV_MODE')
ALLOWED_HOSTS = env("ALLOWED_HOSTS").split(",")
INSTALLED_APPS = [
    "daphne",
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sitemaps',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    "rest_framework",
    "rest_framework.authtoken",
    "corsheaders",
    "django_countries",
    "phonenumber_field",
    'gmailapi_backend',
    'django_celery_results',
    'django_celery_beat',
    'user.apps.UserConfig',
    'shop',
    'notification',
]
INSTALLED_APPS += AUTH_INSTALLED_APPS
'''
These two entries (CELERY_BROKER_URL & CELERY_RESULT_BACKEND) give 
your Celery application instance enough information to know where to 
send messages and where to record the results. Because you’re using 
Redis as both your message broker and your database back end, both 
URLs point to the same address.
'''
# CELERY_BEAT_SCHEDULE = {
#     # for scheduling specific tasks. check contrab.guru
#     "ScheduledEmails": {
#         'task': 'shop.tasks.shop_task_one',
#         'schedule': 10,  # crontab(hour=10, day_of_week=2),
#         'args': ()
#     }
# }
CELERY_BROKER_URL = "redis://127.0.0.1:6379"
CELERY_RESULT_BACKEND = "redis://127.0.0.1:6379"
CELERY_ACCEPT_CONTENT = ['application/json', ]
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TASK_SERIALIZER = 'json'
CELERY_TIMEZONE = 'Africa/Nairobi'
# CELERY_RESULT_BACKEND = 'django-db'
CELERY_CACHE_BACKEND = 'django-cache'
CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler'
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'core.middlewares.ShopMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    "corsheaders.middleware.CorsMiddleware",
]
ROOT_URLCONF = 'core.urls'
ASGI_APPLICATION = 'core.asgi.application'
if not DEBUG:
    CHANNEL_LAYERS = {
        "default": {
            "BACKEND": "channels.layers.InMemoryChannelLayer"
        }
    }
else:
    CHANNEL_LAYERS = {
        "default": {
            "BACKEND": "channels_redis.core.RedisChannelLayer",
            "CONFIG": {
                "hosts": [("127.0.0.1", 6379), ],
            },
        },
    }



TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, "web/templates"),
        ],
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

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
if not DEBUG:
    pass

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator', },
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', },
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator', },
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator', },
]
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATICFILES_DIRS = [os.path.join(BASE_DIR, 'web/static'), ]
STATICFILES_DIRS += AUTH_STATIC
STATIC_URL = "static/"
MEDIA_URL = "media/"
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
MEDIA_ROOT = BASE_DIR / "media/"

STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'

MIDDLEWARE += CORS_MIDDLEWARE
TEMPLATES[0]["OPTIONS"]["context_processors"] += CONTEXT_PROCESSORS

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

EMAIL_HOST_USER = "pmwassini@gmail.com"
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
EMAIL_HOST = "smtp.gmail.com"
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_PORT = 587
EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD")
EMAIL_USE_TLS = True
ALLOWED_EMAIL = ['wingdevelop@gmail.com', 'demo.mail.wing@gmail.com']
CSRF_TRUSTED_ORIGINS = ["http://localhost:3000", ]
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
REST_SESSION_LOGIN = True
# CSRF_COOKIE_SAMESITE = 'Strict'
# SESSION_COOKIE_SAMESITE = 'Strict'
# CSRF_COOKIE_HTTPONLY = False  # False since we will grab it via universal-cookies
# SESSION_COOKIE_HTTPONLY = True

# Setting CSRF_COOKIE_SAMESITE and SESSION_COOKIE_SAMESITE to True prevents cookies and CSRF tokens from being sent
# from any external requests. Setting CSRF_COOKIE_HTTPONLY and SESSION_COOKIE_HTTPONLY to True blocks client-side
# JavaScript from accessing the CSRF and session cookies. We set CSRF_COOKIE_HTTPONLY to False since we'll be
# accessing the cookie via JavaScript.

# If you're in production, you should serve your website over HTTPS and enable CSRF_COOKIE_SECURE and
# SESSION_COOKIE_SECURE, which will only allow the cookies to be sent over HTTPS.
CORS_ALLOWED_ORIGINS = ["http://localhost:3000", ]
CORS_ORIGIN_ALLOW_ALL = False
CORS_ALLOW_HEADERS = (
    'Access-Control-Allow-Origin',
    'Access-Control-Allow-Credentials',
    'Authorization', 'Content-Type',
    'Cache-Control',
    'X-Requested-With',
    'x-csrftoken'
)
# CORS_ALLOW_CREDENTIALS = True
# CSRF_COOKIE_HTTPONLY = False
# SESSION_COOKIE_HTTPONLY = False
# CSRF_USE_SESSIONS = False
# CSRF_COOKIE_SECURE = False
# SESSION_COOKIE_SECURE = False
# SESSION_COOKIE_SAMESITE = 'None'
# CSRF_COOKIE_SAMESITE = 'None'
