

TSD_TYPE = 'Graphite'
GRAPHITE_HOST = '172.17.0.2'
GRAPHITE_INJEST_PORT = 2004
GRAPHITE_HTTP_PORT = 80
OPENTSD_HOST = '127.0.0.1'
OPENTSD_PORT = 4242

CONTRACTOR_HOST = 'http://127.0.0.1:8888'
CONTRACTOR_ROOT_PATH = '/api/v1/'
CONTRACTOR_PROXY = None

PROJECT_PATH = '/home/peter/Projects/t3kton/architect/lib/demo_test/auto_demo_load/'

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '@(a3yjcc(d3uxt)c7n(0vdfhe!$%u2(dvk^9^cg26+4wmih6l7'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

# Application definition

INSTALLED_APPS = (
    'architect.User',
    'architect.Plan',
    'architect.Contractor',
    'architect.TimeSeries',
    'architect.Project',
    'architect.Builder',
    'architect.Inspector',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions'
)

MIDDLEWARE_CLASSES = (
)

ROOT_URLCONF = 'architect.urls'

TEMPLATES = [
]

WSGI_APPLICATION = 'architect.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.8/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'architect',
        'USER': 'architect',
        'PASSWORD': 'architect',
        'HOST': '127.0.0.1',
        'PORT': ''
    }
}


# Internationalization
# https://docs.djangoproject.com/en/1.8/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.8/howto/static-files/

STATIC_URL = '/static/'
