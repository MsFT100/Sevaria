"""
Django settings for sevaria project.

Generated by 'django-admin startproject' using Django 5.1.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.1/ref/settings/
"""

import os
from pathlib import Path

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
                 '127.0.0.1',]


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
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
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

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = '/static/'
STATICFILES_DIRS = [
    BASE_DIR / "static",  # Assuming your static files are in a "static" directory in your project root
]

STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media/'
# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

PESAPAL_SANDBOX_URL = 'https://cybqa.pesapal.com/pesapalv3/api/Auth/RequestToken'
PESAPAL_LIVE_URL = 'https://pay.pesapal.com/v3/api/Auth/RequestToken'
PESAPAL_CONSUMER_KEY = 'RJTyw3yh1GGeEfFYo5T10kiD+1cvjj+T'
PESAPAL_CONSUMER_SECRET = 'nkzkytHx8a3s4b+NwtoxQjnKb1w='
PESAPAL_IPN_URL = 'https://pay.pesapal.com/v3/api/URLSetup/RegisterIPN'
PESAPAL_LIST_IPN_URL = 'https://pay.pesapal.com/v3/api/URLSetup/GetIpnList'
PESAPAL_CALLBACK_URL = 'https://sevariapp-fhe0e8cbfkhxc7hk.eastus-01.azurewebsites.net/paymentresult'
PESAPAL_CHECKOUT_URL = "https://pay.pesapal.com/v3/api/Transactions/SubmitOrderRequest"

CSRF_TRUSTED_ORIGINS = [
    'https://sevariapp-fhe0e8cbfkhxc7hk.eastus-01.azurewebsites.net',
    'https://sevaria.co.ke',
]



