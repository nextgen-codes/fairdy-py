import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# FaiRDy module import
# The FaiRDy module is contained in a folder 'fairdypy' at the same level as the main django project folder
fairdy_module_path = os.path.dirname(BASE_DIR)
sys.path.append(fairdy_module_path)

# TODO isolate for fairdy.no
# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '4c#)$!813^fn&3er35z5(_ff28xuxwlxq&1k$fbbt$g#t%he*_'

# Enable the accounts app to require a user is logged in, and has verified email before running simulations
USE_ACCOUNTS_APP = True
REQUIRE_EMAIL_VERIFICATION = True
ENFORCE_BLOCK_CYCLE_LIMIT = True

# SMTP server used to send email validation messages
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'broremann.ux.uis.no'

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.0/howto/deployment/checklist/
# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['fairdy.ux.uis.no', '192.168.1.199']


# Application definition
INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'accounts.apps.AccountsConfig',
    'fairdy.apps.FairdyConfig'
    'mod_wsgi.server'

]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'web.urls'

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
                'web.context_processors.get_installed_codes',
            ],
        },
    },
]

WSGI_APPLICATION = 'web.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}


# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/3.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

MESSAGE_STORAGE = 'django.contrib.messages.storage.cookie.CookieStorage'


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static"),
]
STATIC_URL = '/static/'
STATIC_ROOT = '/home/prosjekt/fairdy/fairdy-py/web/www/static/'
