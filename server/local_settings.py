import os

# SECURITY WARNING: don't run with debug turned on in production!
import os

PROJECT_PATH = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

DEBUG = True

STATIC_ROOT = '/home/ignite_it/pythonApps/envApi/static'

ALLOWED_HOSTS = ['localhost', '*']
CORS_ORIGIN_ALLOW_ALL = True
# CORS_ORIGIN_WHITELIST = (
#     'localhost:4200',
#     'localhost:8000'
# )

DATABASES = {
    # 'default': {
    #     'ENGINE': 'django.db.backends.postgresql_psycopg2',
    #     'NAME': 'server_gsm',
    #     'HOST': 'localhost',
    #     'PORT': '5432',
    #     'USER': 'postgres',
    #     'PASSWORD': 'postgres',
    # }
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(PROJECT_PATH, 'database.sqlite'),
    }
}

SWAGGER_SETTINGS = {
    'LOGIN_URL': 'http://localhost:8000/admin/login',
    'LOGOUT_URL': 'http://localhost:8000/admin/logout'
}
