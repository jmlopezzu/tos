import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE',
                      'treeofscience.settings.development')

from django.conf import settings

app = Celery('treeofscience')

# Load configuration for celery app
app.config_from_object('django.conf.settings')
# Discover for all project
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
