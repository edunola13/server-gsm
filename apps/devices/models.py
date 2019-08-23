# -*- coding: utf-8 -*-
from __future__ import unicode_literals
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

    read_index_sms = models.IntegerField(default=0)
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
            self.last_connection = timezone.now()
            self.save()
            return

        self.status = STATUS_CON
        self.chip_status = TO_CHIP_STATUS[status.get('s')]
        self.last_connection = timezone.now()
        self.save()

        if self.ship_status == CHIP_STATUS_IN_CALL:
            LogDevice.objects.create(
                log_type=LOG_DEVICE_TYPE_IN_CALL,
                status=LOG_DEVICE_STATUS_OK,
                device=self
            )

        if status.get('r') == 1:
            LogDevice.objects.create(
                log_type=LOG_DEVICE_TYPE_CALL,
                status=LOG_DEVICE_STATUS_OK,
                number=status.get('n', None),
                device=self
            )

        if status.get('m') == 1:
            #
            # VER QUE EL NUMERO PUEDE SER MAYOR O MENOS
            # SI ES MENOR, SE RESETEA EL INDEX_SMS A 1 Y SE LEE HASTA EL NUEVO INDICE
            # SI ES MAYOR, SE LEE HASTA EL NUEVO INDICE
            #
            new_index = self.index_sms = int(status.get('i', 1))
            if new_index > self.index_sms:
                # LEER HASTA NUEVO INDICE
                pass
            if new_index < self.index_sms:
                # RESET Y LEER HASTA EL NUEVO INDICE
                pass
            # self.save()
            # for i in range(self.index_sms - 1, self.index_sms):
            #     LogDevice.objects.create(
            #         log_type=LOG_DEVICE_TYPE_NEWSMS,
            #         description=json.dumps({'index': str(i)}),
            #         device=self
            #     )


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

    def can_treat(self):
        return self.status not in ['OK', 'CAN', 'PRO']

    def treat_log(self):
        try:
            self.status = LOG_STATUS_PRO
            self.save()
            self.__internal_treat_log()
            self.status = LOG_STATUS_OK
            self.save()
        except Exception as e:
            self.status = LOG_STATUS_ERR
            print (e)

    def __internal_treat_log():
        gsm = self.device.__get_client()
        if self.log_type == LOG_DEVICE_TYPE_NEWSMS:
            data = json.loads(self.description)
            description = json.dumps(
                gsm.read_sms(self.number, str(data.get('index', "1")))
            )
            LogDevice.objects.create(
                log_type=LOG_DEVICE_TYPE_SMS,
                description=description,
                status=LOG_DEVICE_STATUS_OK,
                # number= SACAR NUMERO DE DESCRIPTION
                device=self
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

    created_at = models.DateTimeField(auto_now_add=True)

    device = models.ForeignKey(Device, on_delete=models.PROTECT,)
    # rule_instance = models.ForeignKey(RuleInstance,
    #                                   on_delete=models.PROTECT, null=True)

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
                gsm.read_sms(self.number, str(data.get('index', "1")))
            )
        if self.log_type == LOG_ACTION_TYPE_DSMS:
            self.response = json.dumps(gsm.delete_sms())
