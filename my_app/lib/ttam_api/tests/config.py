API_CLIENT_ID = 'CLIENT_ID'
API_CLIENT_SECRET = 'CLIENT_SECRET'
API_REDIRECT_PATH = '/oauth_callback/'
API_URL = 'https://api.23andme.com'
API_SCOPE = 'basic names email'
CERT_FILE = 'CERT_FILE'

ROOT_URLCONF = 'tests.urls'

DEBUG = False
TEMPLATE_DEBUG = False

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
)

TEMPLATE_LOADERS = (
    ('django.template.loaders.cached.Loader'),
)

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": "testDB?mode=memory&cache=shared",
        "USER": "",
        "PASSWORD": "",
        "HOST": "",
        "PORT": "",
    },
}

USE_TZ = True
TIME_ZONE = 'UTC'
LOGGING_CONFIG = None
SECRET_KEY = 'SECRET'
