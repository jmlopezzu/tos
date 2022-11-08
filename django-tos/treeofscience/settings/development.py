from .base import *

DEBUG = True


BASE_URL = 'http://localhost:8000'

# Celery testing
CELERY_ALWAYS_EAGER = True
CELERY_EAGER_PROPAGATES_EXCEPTIONS = True

# Database
# https://docs.djangoproject.com/en/1.8/ref/settings/#databases

EMAIL_HOST = 'mailtrap.io'
EMAIL_HOST_USER = 'd857970572367f'
EMAIL_HOST_PASSWORD = '0643fb082b51bb'
EMAIL_PORT = '2525'


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}
