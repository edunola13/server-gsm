import os

# SECURITY WARNING: don't run with debug turned on in production!
import os
from celery.schedules import crontab

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

CELERY_BEAT_SCHEDULE = {
    'device-1': {
        'task': 'apps.devices.tasks.update_status',
        'schedule': 60.0,  # 20 seconds
        'args': (1,)  # ID of device
    },
    'device_check_new_sms-1': {
        'task': 'apps.devices.tasks.check_new_sms',
        'schedule': 60 * 5 - 10,  # 4:50 minutes:seconds
        'args': (1,)  # ID of device
    },
    # 'device_delete_sms-1': {
    #     'task': 'apps.devices.tasks.delete_sms',
    #     'schedule': crontab(hour=7, minute=30),  # All days at 7:30
    #     'args': (1,)  # ID of device
    # },
    'check_check_pending_log_devices-1': {
        'task': 'apps.devices.tasks.check_pending_log_devices',
        'schedule': 60 * 5  # 5 Minutes
    },
    'check_check_pending_log_actions-1': {
        'task': 'apps.devices.tasks.check_pending_log_actions',
        'schedule': 60 * 5  # 5 Minutes
    }
}

SWAGGER_SETTINGS = {
    'LOGIN_URL': 'http://localhost:8000/admin/login',
    'LOGOUT_URL': 'http://localhost:8000/admin/logout'
}
