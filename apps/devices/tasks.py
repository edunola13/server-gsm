from __future__ import absolute_import, unicode_literals
from celery import task

from datetime import datetime, timedelta

from apps.devices.models import Device, LogAction, LogDevice


@task()
def update_status(id):
    device = Device.objects.get(id=id)
    device.update_status()


# @task()
# def check_new_sms(id):
#     device = Device.objects.get(id=id)
#     gsm = device.__get_client()
#     sms = gsm.get_sms(device.index_sms)
#     if status.get('s', None) == 'error':
#         return
#     if status.get('b', None) == '':
#         gsm.delete_sms()


@task()
def check_pending_log_devices():
    try:
        date = datetime.now() - timedelta(min=10)
        logs = LogDevice.objects.filter(
            status__in=['INI', 'ERR'],
            created_at__lte=date
        )
        for log in logs:
            task.apply_async([log.id], countdown=30)
    except Exception as e:
        print (e)


@task()
def check_pending_log_actions():
    try:
        date = datetime.now() - timedelta(min=10)
        logs = LogAction.objects.filter(
            status__in=['INI', 'ERR'],
            created_at__lte=date
        )
        for log in logs:
            execute_action.apply_async([log.id], countdown=30)
    except Exception as e:
        print (e)


@task(
    max_retries=3,
    default_retry_delay=2 * 60,
    autoretry_for=(Exception,)
)
def execute_action(action_id):
    action = LogAction.objects.get(id=action_id)
    if action.can_execute():
        action.execute_action()
