# Django settings for charsiu project.
import os

DEBUG = True
TEMPLATE_DEBUG = DEBUG

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': os.path.join(os.path.dirname(os.path.abspath(__file__)), "db.sqlite3"), # Or path to database file if using sqlite3.
    }
}

ALLOWED_HOSTS = ['*']
TIME_ZONE = 'America/New_York'
USE_TZ = True

STATIC_ROOT = ''
STATIC_URL = '/static/'

STATICFILES_DIRS = (
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "static"),
)

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = '(m5td_^php&2pzffa#x%&#lwuzw)3hk6(mea62#%pv^vc1do)='

TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
)

ROOT_URLCONF = 'charsiu.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'charsiu.wsgi.application'

TEMPLATE_DIRS = (
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates"),
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    'bootstrap_toolkit',
    'charsiu.charsiu_extras',
)