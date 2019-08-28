# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import json

from apps.devices.models import LogDevice, LogAction
from apps.devices.constants import (
    ORIGIN_RULE,
    LOG_DEVICE_TYPE_SMS,
    LOG_ACTION_TYPE_SMS,
)


class RuleStrategy():
    REQUIRED_DATA = {}  # DATA REQUERIDA PARA CREAR LAS REGLAS,
    # NAME, REQUIRED, TYPE, CHILDS (ITERA)

    def __init__(self, rule):
        self.rule = rule

    def check_rule(self, from_date):
        events = self._get_events(from_date)
        for event in events:
            self._apply_rule(event)

    def is_valid_description(cls, description):
        # VALIDAR LA DATA
        raise Exception("Not Implemented")

    def _get_events(self, from_date):
        # BUSCA LO QUE CORRESPONDA
        raise Exception("Not Implemented")

    def _apply_rule(self, event):
        # HACER LO QUE CORRESPONDA Y GENERAR RULE INSTANCE
        # GUARDAR EN DESCRIPTION LO QUE SE HIZO (COMO LOG)
        raise Exception("Not Implemented")


class RuleStrategyRespondSms(RuleStrategy):
    REQUIRED_DATA = {
        'numbers': {'required': False},  # Numero que manda MSG
        'msg': {'required': True},  # Mensaje a enviar
    }

    def is_valid_description(cls, description):
        return 'msg' in description

    def _get_events(selg, from_date):
        logs = LogDevice.objects.filter(
            date_created__gte=from_date,
            log_type=LOG_DEVICE_TYPE_SMS
        )
        # FILTRAR OTRAS COSAS QUE CORRESPONDA
        return logs

    def _apply_rule(self, event):
        data = json.loads(self.rule.description)
        LogAction.objects.create(
            log_type=LOG_ACTION_TYPE_SMS,
            description=json.dumps({'msg': data['msg']}),
            device=self.rule.device,
            number=event.number,
            origin=ORIGIN_RULE
        )


STRATEGY_CLASS_DEV = {
    'RES_SMS': RuleStrategyRespondSms
}
STRATEGY_CLASS_ACT = {
}
