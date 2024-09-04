
import os
from pathlib import Path
import environ
from zoneinfo import ZoneInfo

env = environ.Env(
    DEBUG=(bool, False)  # Set default values and casting
)

environ.Env.read_env()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-1bb&*-@0^&fntdcejz^@r@^aeqxg+-keyh#8@ks+@pv4c_4jd*'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['sevariapp-fhe0e8cbfkhxc7hk.eastus-01.azurewebsites.net', 
                 'sevaria.co.ke',
                 'localhost',
                 '127.0.0.1',
                 '8309-105-161-82-183.ngrok-free.app',]


# Application definition

INSTALLED_APPS = [
    'rest_framework',
    'main',
    'payments',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

MIDDLEWARE = [
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

ROOT_URLCONF = 'sevaria.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'templates'),
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

WSGI_APPLICATION = 'sevaria.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

DATABASES = {
    'default': {
        #'ENGINE': 'django.db.backends.sqlite3',
        #'NAME': BASE_DIR / 'db.sqlite3',
        'ENGINE': env('DB_ENGINE', default='django.db.backends.mysql'),
        'NAME': env('DB_NAME', default='sDB'),
        'USER': env('DB_USER', default='sevariac'),
        'PASSWORD': env('DB_PASSWORD', default='S'),
        'HOST': env('DB_HOST', default='sevaria.co.ke'),
        'PORT': env('DB_PORT', default='3306'),
        'OPTIONS': {
            'init_command': env('DB_OPTIONS', default="SET sql_mode='STRICT_TRANS_TABLES,NO_ENGINE_SUBSTITUTION'")
        },
    }
}



# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Africa/Nairobi'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = '/static/'
STATICFILES_DIRS = [
    BASE_DIR / "static",  # Directory for your static files
]
STATIC_ROOT = BASE_DIR / "staticfiles"  # Directory where static files will be collected

MEDIA_URL = '/media/'  # URL endpoint for media files
MEDIA_ROOT = BASE_DIR / 'media/'
# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

EXCHANGERATE_API = env('EXCHANGERATE_API')
SHIPSHAP_API_TOKEN = env('SHIPSHAP_API_TOKEN')
PESAPAL_SANDBOX_URL = env('PESAPAL_SANDBOX_URL')
PESAPAL_LIVE_URL = env('PESAPAL_LIVE_URL')
PESAPAL_CONSUMER_KEY = env('PESAPAL_CONSUMER_KEY')
PESAPAL_CONSUMER_SECRET = env('PESAPAL_CONSUMER_SECRET')
PESAPAL_IPN_URL = env('PESAPAL_IPN_URL')
PESAPAL_LIST_IPN_URL = env('PESAPAL_LIST_IPN_URL')
PESAPAL_CALLBACK_URL = env('PESAPAL_CALLBACK_URL')
PESAPAL_CHECKOUT_URL = env("PESAPAL_CHECKOUT_URL")
IPN_ID = env('IPN_ID')

CSRF_TRUSTED_ORIGINS = [
    'https://f150-41-212-45-223.ngrok-free.app',
    'https://sevaria.co.ke',
]

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'mail.sevaria.co.ke'  # Remove the comma
EMAIL_PORT = 465
EMAIL_USE_SSL = True  # Use SSL for port 465
EMAIL_USE_TLS = False  # Disable TLS
EMAIL_HOST_USER = 'hello@sevaria.co.ke'
EMAIL_HOST_PASSWORD = 'Jl959js$6'
DEFAULT_FROM_EMAIL = 'hello@sevaria.co.ke'




