from __future__ import absolute_import, unicode_literals
from celery import task

from datetime import datetime, timedelta

from apps.devices.models import Device, LogAction, LogDevice

from server.redis_lock import Lock


@task()  # 15 Segs
def update_status(id):
    # Acorto retry y delay para que basicamente ignoremos la task asi no se apilan
    with Lock('TASK_DEVICE_ID_%d' % id, 2000, 0, 0.2):
        device = Device.objects.get(id=id)
        device.update_status()


@task()  # 5 Mins / No ejecutar al mismo tiempo que update_status
def check_new_sms(id):
    with Lock('TASK_DEVICE_ID_%d' % id, 60000):
        device = Device.objects.get(id=id)
        device.check_new_sms()


@task()  # Una vez al dia / No ejecutar al mismo tiempo que update_status
def delete_sms(id):
    with Lock('TASK_DEVICE_ID_%d' % id, 60000):
        device = Device.objects.get(id=id)
        device.delete_sms()


@task()
def check_pending_log_devices():
    logs = LogDevice.objects.filter(
        status__in=['INI', 'ERR']
    )
    time = 2
    for log in logs:
        treat_log_device.apply_async([log.id], countdown=10 + time)
        time += 5


@task(
    max_retries=3,
    default_retry_delay=2 * 60,
    autoretry_for=(Exception,)
)
def treat_log_device(action_id):
    log = LogDevice.objects.get(id=action_id)
    if log.can_treat():
        log.treat_log()


@task()
def check_pending_log_actions():
    date = datetime.now() - timedelta(min=10)
    logs = LogAction.objects.filter(
        status__in=['INI', 'ERR'],
        created_at__lte=date
    )
    for log in logs:
        execute_action.apply_async([log.id], countdown=30)


@task(
    max_retries=3,
    default_retry_delay=2 * 60,
    autoretry_for=(Exception,)
)
def execute_action(action_id):
    action = LogAction.objects.get(id=action_id)
    if action.can_execute():
        action.execute_action()
