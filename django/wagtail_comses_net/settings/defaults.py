"""
Django settings for wagtail_comses_net project.

Generated by 'django-admin startproject' using Django 1.10.4.

For more information on this file, see
https://docs.djangoproject.com/en/1.10/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.10/ref/settings/
"""

from __future__ import absolute_import, unicode_literals

import configparser
import os

# go two levels up for root project directory
PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# base directory is one level above the project directory
BASE_DIR = os.path.dirname(PROJECT_DIR)

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.10/howto/deployment/checklist/

# Application definition
WAGTAIL_APPS = [
    'wagtail.wagtailforms',
    'wagtail.wagtailredirects',
    'wagtail.wagtailembeds',
    'wagtail.wagtailsites',
    'wagtail.wagtailusers',
    'wagtail.wagtailsnippets',
    'wagtail.wagtaildocs',
    'wagtail.wagtailimages',
    'wagtail.wagtailsearch',
    'wagtail.wagtailadmin',
    'wagtail.wagtailcore',
    'wagtail.contrib.modeladmin',
    'wagtailmenus',
    'modelcluster',
    'taggit',
    'search',
]
DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_extensions',
    'timezone_field',
    'rest_framework',
    'rest_framework_swagger',
    'webpack_loader',
]

COMSES_APPS = [
    'library',
    'home',
    'citation',
]

INSTALLED_APPS = WAGTAIL_APPS + DJANGO_APPS + COMSES_APPS

MIDDLEWARE = [
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',

    'wagtail.wagtailcore.middleware.SiteMiddleware',
    'wagtail.wagtailredirects.middleware.RedirectMiddleware',
]


ROOT_URLCONF = 'wagtail_comses_net.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(PROJECT_DIR, 'templates'),
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'wagtail.contrib.settings.context_processors.settings',
                'wagtailmenus.context_processors.wagtailmenus',
            ],
        },
    },
]

WSGI_APPLICATION = 'wagtail_comses_net.wsgi.application'

# Database
# https://docs.djangoproject.com/en/1.10/ref/settings/#databases

config = configparser.ConfigParser()
config.read('/secrets/config.ini')

SECRET_KEY = config.get('secrets', 'SECRET_KEY')

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config.get('database', 'DB_NAME'),
        'USER': config.get('database', 'DB_USER'),
        'PASSWORD': config.get('database', 'DB_PASSWORD'),
        'HOST': config.get('database', 'DB_HOST'),
        'PORT': config.get('database', 'DB_PORT'),
        'ATOMIC_REQUESTS': True,
    }
}

LOG_DIRECTORY = config.get('logging', 'LOG_DIRECTORY', fallback=os.path.join(BASE_DIR, 'logs'))
LIBRARY_ROOT = config.get('storage', 'LIBRARY_ROOT', fallback=os.path.join(BASE_DIR, 'library'))
REPOSITORY_ROOT = config.get('storage', 'REPOSITORY_ROOT', fallback=os.path.join(BASE_DIR, 'repository'))

for d in (LOG_DIRECTORY, LIBRARY_ROOT, REPOSITORY_ROOT):
    try:
        if not os.path.isdir(d):
            os.mkdir(d)
    except OSError:
        print("Unable to create directory", d)

# logging configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'root': {
        'level': 'ERROR',
        'handlers': ['rollingfile', 'console'],
    },
    'formatters': {
        'verbose': {
            'format': '%(asctime)s %(levelname)-7s %(name)s:%(funcName)s:%(lineno)d %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S'
        },
        'simple': {
            'format': "%(levelname)-8s %(message)s"
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'DEBUG',
            'formatter': 'verbose'
        },
        'rollingfile': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'formatter': 'verbose',
            'filename': os.path.join(LOG_DIRECTORY, 'comsesnet.log'),
            'backupCount': 6,
            'maxBytes': 10000000,
        },
    },
    'loggers': {
        'home': {
            'level': 'DEBUG',
            'handlers': ['console'],
            'propagate': False
        },
        'library': {
            'level': 'DEBUG',
            'handlers': ['console', 'rollingfile'],
            'propagate': False,
        },
        'drupal_migrator': {
            'level': 'DEBUG',
            'handlers': ['console', 'rollingfile'],
            'propagate': False,
        }
    }
}


# Internationalization
# https://docs.djangoproject.com/en/1.10/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.10/howto/static-files/

STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
]

WEBPACK_DIR = '/webpack'

STATICFILES_DIRS = [
    WEBPACK_DIR
]

STATIC_ROOT = '/static'
STATIC_URL = '/static/'

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'


# Wagtail settings

WAGTAIL_SITE_NAME = "wagtail_comses_net"

WEBPACK_LOADER = {
    'DEFAULT': {
        'BUNDLE_DIR_NAME': 'assets/',
        'STATS_FILE': os.path.join(WEBPACK_DIR, 'webpack-stats.json'),
    }
}

# Base URL to use when referring to full URLs within the Wagtail admin backend -
# e.g. in notification emails. Don't include '/admin' or a trailing slash
BASE_URL = 'https://www.comses.net'

WAGTAILMENUS_DEFAULT_MAIN_MENU_TEMPLATE = 'home/includes/menu.html'

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': ('rest_framework.permissions.IsAdminUser',),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework_jwt.authentication.JSONWebTokenAuthentication',
    ),
    'PAGE_SIZE': 10
}
