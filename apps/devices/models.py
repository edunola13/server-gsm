# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import logging
import json

from django.utils import timezone

from django.db import models

from .constants import *

from apps.devices.client import GSMClient


class Device (models.Model):
    name = models.CharField(max_length=100)
    number = models.CharField(max_length=30)
    chip_id = models.CharField(max_length=100, blank=True, null=True)
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default=STATUS_INI)
    chip_status = models.CharField(
        max_length=10,
        choices=CHIP_STATUS_CHOICES,
        default=CHIP_STATUS_FREE)

    index_sms = models.IntegerField(default=0)
    channel_i2c = models.CharField(max_length=10)
    last_connection = models.DateTimeField(null=True)
    enabled = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def _get_client(self):
        return GSMClient(int(self.channel_i2c))

    def update_status(self):
        gsm = self._get_client()
        status = gsm.get_status()
        if status.get('s', None) == 'error':
            LogDevice.create(
                LOG_DEVICE_TYPE_ERR,
                self,
                LOG_DEVICE_STATUS_OK
            )
            self.status = STATUS_ERR
            self.last_connection = timezone.now()
            self.save()
            return

        self.status = STATUS_CON
        self.chip_status = TO_CHIP_STATUS[status.get('s')]
        self.last_connection = timezone.now()
        self.save()

        if self.chip_status == CHIP_STATUS_IN_CALL:
            LogDevice.create(
                LOG_DEVICE_TYPE_IN_CALL,
                self,
                LOG_DEVICE_STATUS_OK
            )

        if status.get('r') == 1:
            LogDevice.create(
                LOG_DEVICE_TYPE_CALL,
                self,
                LOG_DEVICE_STATUS_OK,
                status.get('n', None)
            )

        if status.get('m') == 1:
            new_index = int(status.get('i', 1))
            if new_index > self.index_sms:
                for i in range(self.index_sms + 1, new_index + 1):
                    log = LogDevice.create(
                        LOG_DEVICE_TYPE_NEWSMS,
                        self,
                        description=json.dumps({'index': str(i)})
                    )
                    log.launch_task()
            if new_index < self.index_sms:
                for i in range(1, new_index + 1):
                    log = LogDevice.create(
                        LOG_DEVICE_TYPE_NEWSMS,
                        self,
                        description=json.dumps({'index': str(i)})
                    )
                    log.launch_task()
            self.index_sms = new_index
            self.save()

            if new_index > 20:
                self.launch_delete_sms(10)

    def check_new_sms(self):
        gsm = self._get_client()
        index = self.index_sms + 1
        for i in range(25):  # Leo maximo X mensajes en un tasks
            sms = gsm.get_sms(str(index))
            if sms.get('s', None) == 'error':
                break
            if sms.get('b', None) == '':
                break
            if sms.get('b', None) != '':
                log = LogDevice.create(
                    LOG_DEVICE_TYPE_NEWSMS,
                    self,
                    description=json.dumps({'index': str(i)})
                )
                self.index_sms = index
                self.save()
                log.launch_task()
            index += 1

    def delete_sms(self):
        gsm = self._get_client()
        gsm.delete_sms()
        # Leo con el indice anterior por si aparecio alguno nuevo
        self.check_new_sms()
        # Reseteo el indice
        self.index_sms = 0
        self.save()

    def launch_delete_sms(self, countdown=0.25):
        from apps.devices.tasks import delete_sms
        delete_sms.apply_async([self.id], countdown=countdown)


class LogDevice (models.Model):
    status = models.CharField(
        max_length=10,
        choices=LOG_DEVICE_STATUS_CHOICES,
        default=LOG_DEVICE_STATUS_INI)
    log_type = models.CharField(max_length=10, choices=LOG_DEVICE_TYPE_CHOICES)
    number = models.CharField(max_length=100, null=True)
    description = models.TextField(null=True)

    date_ok = models.DateTimeField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    device = models.ForeignKey(Device, on_delete=models.PROTECT,)

    @classmethod
    def create(cls, log_type, device, status=LOG_DEVICE_STATUS_INI, number=None, description=None):
        log = LogDevice.objects.create(
            log_type=log_type,
            status=status,
            number=number,
            description=description,
            device=device
        )
        if log.log_type == LOG_DEVICE_TYPE_SMS:
            log.number = log.get_number_of_sms()
            log.save()
        if log.status == 'OK':
            log.date_ok = timezone.now()
            log.save()
            log.launch_rule()
        return log

    def get_description(self):
        try:
            return json.loads(self.description)
        except Exception:
            return None

    def get_number_of_sms(self):
        try:
            return self.get_description()['b'].split('\r\n')[0].split(',')[1].strip("'")
        except Exception:
            return None

    def get_msg_of_sms(self):
        try:
            return self.get_description()['b'].split('\r\n')[1]
        except Exception:
            return None

    def can_update(self):
        return self.status not in ['OK', 'CAN', 'PRO']

    def can_treat(self):
        return self.status in [LOG_DEVICE_STATUS_INI, LOG_DEVICE_STATUS_ERR]

    def launch_task(self, countdown=0.25):
        from apps.devices.tasks import treat_log_device
        treat_log_device.apply_async([self.id], countdown=countdown)

    def launch_rule(self, countdown=0.25):
        from apps.devices.tasks import execute_rule_log_device
        execute_rule_log_device.apply_async([self.id], countdown=countdown)

    def treat_log(self):
        try:
            self.status = LOG_DEVICE_STATUS_PRO
            self.save()
            self.__internal_treat_log()
            self.date_ok = timezone.now()
            self.status = LOG_DEVICE_STATUS_OK
            self.save()
            self.launch_rule()
        except Exception as e:
            self.status = LOG_DEVICE_STATUS_ERR
            self.save()
            logging.error("TREAT_LOG log_device %d, error %s" % (self.id, e))
            raise e

    def __internal_treat_log(self):
        gsm = self.device._get_client()
        if self.log_type == LOG_DEVICE_TYPE_NEWSMS:
            data = json.loads(self.description)
            description = gsm.get_sms(str(data.get('index', "1")))
            description['index'] = data.get('index', "1")
            description['log_device'] = self.id
            LogDevice.create(
                LOG_DEVICE_TYPE_SMS,
                self.device,
                LOG_DEVICE_STATUS_OK,
                description=json.dumps(description)
            )


class LogAction (models.Model):
    status = models.CharField(
        max_length=10,
        choices=LOG_ACTION_STATUS_CHOICES,
        default=LOG_ACTION_STATUS_INI)
    origin = models.CharField(max_length=10, choices=ORIGIN_CHOICES)
    log_type = models.CharField(max_length=10, choices=LOG_ACTION_TYPE_CHOICES)
    number = models.CharField(max_length=100, null=True)
    description = models.TextField(null=True)
    response = models.TextField(null=True)

    date_ok = models.DateTimeField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    device = models.ForeignKey(Device, on_delete=models.PROTECT,)

    @classmethod
    def create(cls, log_type, device, origin, status=LOG_ACTION_STATUS_INI, number=None, description=None):
        log = LogAction.objects.create(
            log_type=log_type,
            origin=origin,
            status=status,
            number=number,
            description=description,
            device=device
        )
        if log.status == 'OK':
            log.date_ok = timezone.now()
            log.save()
            log.launch_rule()
        return log

    def get_description(self):
        try:
            return json.loads(self.description)
        except Exception:
            return None

    def get_response(self):
        try:
            return json.loads(self.response)
        except Exception:
            return None

    def can_update(self):
        return self.status not in ['OK', 'CAN', 'PRO']

    def can_execute(self):
        return self.status in [LOG_ACTION_STATUS_INI, LOG_ACTION_STATUS_ERR]

    def launch_task(self, countdown=1):
        from apps.devices.tasks import execute_action
        execute_action.apply_async([self.id], countdown=countdown)

    def launch_rule(self, countdown=0.25):
        from apps.devices.tasks import execute_rule_log_action
        execute_rule_log_action.apply_async([self.id], countdown=countdown)

    def execute_action(self):
        try:
            self.status = LOG_ACTION_STATUS_PRO
            self.save()
            self.__internal_execute_action()
            self.date_ok = timezone.now()
            self.status = LOG_ACTION_STATUS_OK
            self.save()
            self.launch_rule()
        except Exception as e:
            self.status = LOG_ACTION_STATUS_ERR
            self.save()
            logging.error("TREAT_LOG log_action %d, error %s" % (self.id, e))

    def __internal_execute_action(self):
        gsm = self.device._get_client()

        if self.log_type == LOG_ACTION_TYPE_CALL:
            self.response = json.dumps(gsm.make_call(self.number))
        if self.log_type == LOG_ACTION_TYPE_ANSW:
            self.response = json.dumps(gsm.answer_call())
        if self.log_type == LOG_ACTION_TYPE_HOFF:
            self.response = json.dumps(gsm.hangoff_call())
        if self.log_type == LOG_ACTION_TYPE_SMS:
            data = json.loads(self.description)
            self.response = json.dumps(
                gsm.send_sms(self.number, data.get('msg', ''))
            )
        if self.log_type == LOG_ACTION_TYPE_RSMS:
            data = json.loads(self.description)
            self.response = json.dumps(
                gsm.get_sms(str(data.get('index', "1")))
            )
        if self.log_type == LOG_ACTION_TYPE_DSMS:
            self.response = json.dumps(gsm.delete_sms())
        if self.log_type == LOG_ACTION_TYPE_INFO:
            self.response = json.dumps(gsm.get_info())
        if self.log_type == LOG_ACTION_TYPE_STA:
            self.response = json.dumps(gsm.get_status())
