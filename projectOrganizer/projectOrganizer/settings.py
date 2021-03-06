"""
Django settings for projectOrganizer project.

Generated by 'django-admin startproject' using Django 1.9.4.

For more information on this file, see
https://docs.djangoproject.com/en/1.9/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.9/ref/settings/
"""

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.9/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '#p%n5@@o*_rmd_a5#!t(rwj5$cqyfq0pl&7#5hs3)1h7mumaj$'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []



# Application definition

INSTALLED_APPS = [
    'pjo.apps.PjoConfig',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

MIDDLEWARE_CLASSES = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'pjo.middleware.AutoLogout',
    'pjo.middleware.ExceptionHandler',
]

ROOT_URLCONF = 'projectOrganizer.urls'

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

WSGI_APPLICATION = 'projectOrganizer.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.9/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'USER': 'root',
        'NAME': 'pjodb',
        'PASSWORD':'hello',
        'HOST': '127.0.0.1',
        'PORT': '3306',
    }
}


# Password validation
# https://docs.djangoproject.com/en/1.9/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/1.9/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'America/New_York'

USE_I18N = True

USE_L10N = True

USE_TZ = True




# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.9/howto/static-files/

STATIC_URL = '/static/'


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'formatters': {
        'simple': {
            'format': '[%(levelname)s](line:%(lineno)d) (%(module)s.%(funcName)s) %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S'
        },
        'verbose': {
            'format': '[%(asctime)s][%(levelname)s] %(module)s.%(funcName)s(line:%(lineno)d) %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S'
        },
        'dbFormat': {
            'format': '[%(asctime)s][%(levelname)s] %(module)s.%(funcName)s(line:%(lineno)d) \n %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S'
        },
        'errFormat': {
            'format': '[%(asctime)s][%(levelname)s] %(module)s.%(funcName)s(line:%(lineno)d)[th:%(thread)d,prc:%(process)d]  %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S'
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'filters': ['require_debug_true'],
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
        'devLogFileForServer': {
            'level': 'DEBUG',
            'filters': ['require_debug_true'],
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'filename': '/pjoLog/pjoDev.log', 
            'when': 'D',
            'interval': 1,
            'backupCount': 10,
            'formatter': 'verbose'
        },
        'devLogFile': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': '/pjoLog/pjoDev.log', 
            'formatter': 'verbose'
        },
        'dbLogFile': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': '/pjoLog/pjoDB.log',
            'formatter': 'dbFormat'
        },
        'errLogFile': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': '/pjoLog/pjoError.log',
            'formatter': 'errFormat'
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'propagate': True,
        },
        'django.request': {
            'handlers': ['console'],
#             'handlers': ['console', 'errLogFile'],
            'propagate': False,
            'level': 'ERROR',
        },
        'dba': {
#             'handlers': ['console', 'dbLogFile'],
            'handlers': ['console'],
            'level': 'DEBUG',
        },
        'devLog': {
#             'handlers': ['console', 'devLogFile'],
            'handlers': ['console'],
            'level': 'DEBUG',
        },
        'errLog': {
#             'handlers': ['console', 'errLogFile'],
            'handlers': ['console'],
            'level': 'ERROR',
        },
    }
}



######################################################################
## ADDED
######################################################################

# For Auto Logout
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_SERIALIZER = 'django.contrib.sessions.serializers.PickleSerializer'
AUTO_LOGOUT_DELAY = 20



