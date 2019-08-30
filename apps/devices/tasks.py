from __future__ import absolute_import, unicode_literals
import logging
from celery import task

from django.utils import timezone
from datetime import datetime, timedelta

from apps.devices.models import Device, LogAction, LogDevice
from apps.rules.models import Rule

from server.redis_lock import Lock


@task()  # 15 Segs
def update_status(id):
    try:
        # Acorto retry y delay para que basicamente ignoremos la task asi no se apilan
        with Lock('TASK_DEVICE_ID_%d' % id, 2000, 0, 0.2):
            device = Device.objects.get(id=id)
            device.update_status()
    except Exception as e:
        logging.error("UPDATE_STATUS device %d, error %s" % (id, e))


@task()  # 5 Mins / No ejecutar al mismo tiempo que update_status
def check_new_sms(id):
    try:
        with Lock('TASK_DEVICE_ID_%d' % id, 60000):
            device = Device.objects.get(id=id)
            device.check_new_sms()
    except Exception as e:
        logging.error("CHECK_NEW_SMS device %d, error %s" % (id, e))


@task()  # Una vez al dia / No ejecutar al mismo tiempo que update_status
def delete_sms(id):
    try:
        with Lock('TASK_DEVICE_ID_%d' % id, 60000):
            device = Device.objects.get(id=id)
            device.delete_sms()
    except Exception as e:
        logging.error("DELETE_SMS device %d, error %s" % (id, e))


@task()
def check_pending_log_devices():
    date = datetime.now() - timedelta(min=10)
    logs = LogDevice.objects.filter(
        status__in=['INI', 'ERR'],
        created_at__lte=date
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
    try:
        log = LogDevice.objects.get(id=action_id)
        if log.can_treat():
            log.treat_log()
    except Exception as e:
        logging.error("TREAT_LOG_DEVICE action %d, error %s" % (action_id, e))


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
    try:
        action = LogAction.objects.get(id=action_id)
        if action.can_execute():
            action.execute_action()
    except Exception as e:
        logging.error("EXECUTE_ACTION action %d, error %s" % (action_id, e))


@task()
def execute_rules(device_id):
    #
    # VER SI APLICAR ASI DE FORMA QUE BUSQUE TODAS LAS ACCIONES QUE PASARON O QUE PASEN
    # DIRECTAMENTE EL ID DE LA ACCION
    #
    rules = Rule.objects.filter(
        device__id=device_id,
        enabled=True
    )
    device = Device.objects.get(id=id)
    device.last_rule_date = timezone.now()
    device.save()
    for rule in rules:
        try:
            rule.check_rule(rule.device.last_rule_date)
        except Exception as e:
            logging.error("EXECUTE_RULES device %d, error %s" % (device_id, e))
