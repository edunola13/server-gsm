from __future__ import absolute_import, unicode_literals
import json
from celery import task

from datetime import datetime, timedelta

from apps.devices.models import Device, LogAction, LogDevice
from apps.devices.constants import LOG_DEVICE_TYPE_NEWSMS


@task()  # 15 Segs
def update_status(id):
    device = Device.objects.get(id=id)
    device.update_status()


@task()  # 5 Mins / No ejecutar al mismo tiempo que update_status
def check_new_sms(id):
    device = Device.objects.get(id=id)
    gsm = device.__get_client()
    index = device.index_sms + 1
    for i in range(25):  # Leo maximo X mensajes en un tasks
        sms = gsm.get_sms(index)
        if sms.get('s', None) == 'error':
            break
        if sms.get('b', None) == '':
            break
        if sms.get('b', None) != '':
            device.index_sms = index
            device.save()
            LogDevice.objects.create(
                log_type=LOG_DEVICE_TYPE_NEWSMS,
                description=json.dumps({'index': index}),
                device=device
            )
        index += 1


@task()  # X Dias / No ejecutar al mismo tiempo que update_status
def delete_sms(id):
    device = Device.objects.get(id=id)
    gsm = device.__get_client()
    gsm.delete_sms()
    # Leo con el indice anterior por si aparecio alguno nuevo
    check_new_sms(id)
    # Reseteo el indice
    device.index_sms = 1
    device.save()


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
