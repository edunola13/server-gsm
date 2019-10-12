# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import logging
import json

from apps.devices.models import LogDevice, LogAction
from apps.devices.constants import (
    ORIGIN_RULE,
    LOG_DEVICE_TYPE_SMS, LOG_DEVICE_TYPE_CALL,
    LOG_ACTION_TYPE_SMS, LOG_ACTION_STATUS_INI
)

logger = logging.getLogger('log_devices')


class RuleStrategy():
    REQUIRED_DATA = {}  # DATA REQUERIDA PARA CREAR LAS REGLAS,
    # NAME, REQUIRED, TYPE, CHILDS (ITERA)

    def __init__(self, rule):
        self.rule = rule

    def check_rule(self, event):
        if self._is_valid_event(event):
            self._apply_rule(event)

    @classmethod
    def is_valid_description(cls, description):
        # VALIDAR LA DATA
        raise Exception("Not Implemented")

    def _is_valid_event(self, event):
        # CHEQUEAR QUE EL EVENTO SEA MANEJABLE
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

    @classmethod
    def is_valid_description(cls, description):
        return 'msg' in description

    def _is_valid_event(self, event):
        if event.log_type != LOG_DEVICE_TYPE_SMS:
            return False

        data = self.rule.get_description()
        if 'numbers' in data:
            if event.number not in data['numbers']:
                return False

        return True

    def _apply_rule(self, event):
        try:
            from apps.rules.models import RuleInstance
            data = json.loads(self.rule.description)
            action = LogAction.create(
                LOG_ACTION_TYPE_SMS,
                self.rule.device,
                ORIGIN_RULE,
                LOG_ACTION_STATUS_INI,
                event.number,
                json.dumps({'msg': data['msg']})
            )
            RuleInstance.objects.create(
                rule=self.rule,
                description=json.dumps({'actions': [action.id]}),
                thrower=event
            )
            action.launch_task()
        except Exception as e:
            RuleInstance.objects.create(
                rule=self.rule,
                description=json.dumps({'data': e}),
                is_ok=False,
                thrower=event
            )


class RuleStrategyListenAndLog(RuleStrategy):
    REQUIRED_DATA = {
    }

    @classmethod
    def is_valid_description(cls, description):
        return True

    def _is_valid_event(self, event):
        if event.log_type in [LOG_DEVICE_TYPE_SMS, LOG_DEVICE_TYPE_CALL]:
            return True
        return False

    def _apply_rule(self, event):
        try:
            from apps.rules.models import RuleInstance

            logger.info("NEW {} FROM {}".format(event.log_type, event.number))

            RuleInstance.objects.create(
                rule=self.rule,
                description=json.dumps(
                    {'data': "NEW {} FROM {}".format(event.log_type, event.number)}
                ),
                thrower=event
            )
        except Exception as e:
            RuleInstance.objects.create(
                rule=self.rule,
                description=json.dumps({'data': e}),
                is_ok=False,
                thrower=event
            )


STRATEGY_CLASS_DEV = {
    'RES_SMS': RuleStrategyRespondSms,
    'LIS_LOG': RuleStrategyListenAndLog
}
STRATEGY_CLASS_ACT = {
}
