# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from datetime import datetime

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

    index_sms = models.IntegerField(default=1)
    channel_i2c = models.CharField(max_length=10)
    last_connection = models.DateTimeField(null=True)
    enabled = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __get_client(self):
        return GSMClient(int(self.channel_i2c))

    def update_status(self):
        gsm = self.__get_client()
        status = gsm.get_status()
        if status.get('s', None) == 'error':
            LogDevice.objects.create(
                log_type=LOG_DEVICE_TYPE_ERR,
                device=self
            )
            self.status = STATUS_ERR
            self.last_connection = datetime.now()
            self.save()
            return

        self.status = STATUS_CON
        self.chip_status = TO_CHIP_STATUS[status.get('s')]
        self.last_connection = datetime.now()
        self.save()

        if status.get('r') == 1:
            LogDevice.objects.create(
                log_type=LOG_DEVICE_TYPE_CALL,
                number=status.get('n', None),
                device=self
            )

        if status.get('m') == 1:
            LogDevice.objects.create(
                log_type=LOG_DEVICE_TYPE_SMS,
                description=json.dumps({'index': status.get('i')}),
                device=self
            )


class LogDevice (models.Model):
    status = models.CharField(
        max_length=10,
        choices=LOG_DEVICE_STATUS_CHOICES,
        default=LOG_DEVICE_STATUS_INI)
    log_type = models.CharField(max_length=10, choices=LOG_DEVICE_TYPE_CHOICES)
    number = models.CharField(max_length=100, null=True)
    description = models.TextField(null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    device = models.ForeignKey(Device, on_delete=models.PROTECT,)

    def get_description(self):
        try:
            return json.loads(serializer.instance.description)
        except Exception:
            return None

    def can_update(self):
        return self.status not in ['OK', 'CAN', 'PRO']

    """
        Los LogDevice tambien van a tener estado y se van a ejecutar
        En base a los LogDevice y LogAction se sabe todo.
        Despues vamos a tener 2 modelos mas llamados SMS (entrada y salida) y Call (entrada y salida)
        estos se van a generar en base a los log.
        Ver bien en base a que hacer las reglas.
    """


class Rule (models.Model):
    name = models.CharField(max_length=100)
    origin = models.CharField(max_length=10, choices=ORIGIN_CHOICES)
    rule_type = models.CharField(max_length=10, choices=RULE_TYPE_CHOICES, default=RULE_TYPE_DEFAULT)
    from_type = models.CharField(max_length=10, choices=RULE_FROM_TYPE_CHOICES, null=True)
    from_number = models.CharField(max_length=255, null=True)
    to_type = models.CharField(max_length=10, choices=RULE_TO_TYPE_CHOICES, null=True)
    to_number = models.CharField(max_length=255, null=True)
    enabled = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    device = models.ForeignKey(Device, related_name='rules', on_delete=models.PROTECT,)  # Puede no tener device


class RuleInstance (models.Model):
    description = models.TextField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    log_device = models.ForeignKey(LogDevice, on_delete=models.PROTECT,)
    rule = models.ForeignKey(Rule, on_delete=models.PROTECT,)


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

    created_at = models.DateTimeField(auto_now_add=True)

    device = models.ForeignKey(Device, on_delete=models.PROTECT,)
    rule_instance = models.ForeignKey(RuleInstance,
                                      on_delete=models.PROTECT, null=True)

    def get_description(self):
        try:
            return json.loads(serializer.instance.description)
        except Exception:
            return None

    def get_response(self):
        try:
            return json.loads(serializer.instance.response)
        except Exception:
            return None

    def can_update(self):
        return self.status not in ['OK', 'CAN', 'PRO']

    def can_execute(self):
        return self.status in [LOG_STATUS_INI, LOG_STATUS_ERR]

    def execute_action(self):
        try:
            self.status = LOG_STATUS_PRO
            self.save()
            self.__internal_execute_action()
            self.status = LOG_STATUS_OK
            self.save()
        except Exception as e:
            self.status = LOG_STATUS_ERR
            print (e)

    def __internal_execute_action(self):
        gsm = self.device.__get_client()
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
                gsm.read_sms(self.number, data.get('index', "1"))
            )
