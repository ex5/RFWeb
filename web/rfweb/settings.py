# Django settings for RFWeb project.
# 

import os
import sys

# Path to the directory containing this file. Don't edit!
_BASEDIR = os.path.dirname(__file__)
APPLICATION_DIR = os.path.dirname(_BASEDIR)
PROJECT_NAME = os.path.basename(_BASEDIR)
APPEND_SLASH = False

DEBUG = True
TEMPLATE_DEBUG = DEBUG
DAJAXICE_MEDIA_PREFIX = "dajaxice"
DAJAXICE_DEBUG = True
DAJAXICE_JS_DOCSTRINGS = True
DAJAXICE_NOTIFY_EXCEPTIONS = True

TIME_ZONE = 'Europe/Moscow'
ADMINS = (
    ('Anna Sirota', 'anna.sirota@t-platforms.ru'),
)

MANAGERS = ADMINS
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'USER': PROJECT_NAME,
        'PASSWORD': '123456',
        'NAME': PROJECT_NAME,
        'HOST': 'qa-master',
        'PORT': '',
        'OPTIONS': {
               'init_command': 'SET storage_engine=MYISAM,character_set_connection=utf8,collation_connection=utf8_unicode_ci'
               }
    }
}

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = False

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = os.path.join(_BASEDIR, 'media')
SUITS_PATH = os.path.join(MEDIA_ROOT, 'suits')
RESULTS_PATH = os.path.join(MEDIA_ROOT, 'results')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = 'http://192.168.100.146:8181/media/'

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = 'media/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'pmst_958#g=ks#i+(ci!pnf5=1b73@nf(c%h8)p&sc7wongki6'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
    'django.template.loaders.eggs.Loader',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.static",
    "django.core.context_processors.request",
    "django.contrib.messages.context_processors.messages",
)


MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.gzip.GZipMiddleware',
)

ROOT_URLCONF = 'rfweb.urls'

# Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
# Always use forward slashes, even on Windows.
# Don't forget to use absolute paths, not relative paths.
TEMPLATE_DIRS = (
    os.path.join(_BASEDIR, 'rfwebapp', 'templates').replace('\\', '/'),
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.admin',
    'dajaxice',
    'dajax',
    'rfweb.rfwebapp'
)

import logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)s %(name)s %(message)s')

