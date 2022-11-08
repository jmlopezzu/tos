# -*- coding: utf-8 -*-
from .base import *

DEBUG = False

ALLOWED_HOSTS = ['.unal.edu.co', '.mytreeofscience.com', ]

MEDIA_ROOT = '/home/django/media/'

STATIC_ROOT = '/home/django/static/'

BASE_URL = 'http://unal.mytreeofscience.com'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': CONFIG_PARSER['database']['DB_NAME'],
        'USER': CONFIG_PARSER['database']['DB_USER'],
        'PASSWORD': CONFIG_PARSER['database']['DB_PASSWORD'],
        'HOST': 'localhost',
        'PORT': '',
    }
}
