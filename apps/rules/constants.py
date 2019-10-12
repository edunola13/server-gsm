# -*- coding: utf-8 -*-
from __future__ import unicode_literals

RULE_STRATEGY_RES_SMS = 'RES_SMS'
RULE_STRATEGY_LISTEN_LOG = 'LIS_LOG'
RULE_STRATEGY_CHOICES = (
    (RULE_STRATEGY_RES_SMS, 'Respond SMS'),
    (RULE_STRATEGY_LISTEN_LOG, 'Listen SMS & CALL'),
)

RULE_TYPE_DEVICE = 'DEV'
RULE_TYPE_ACTION = 'ACT'
RULE_TYPE_CHOICES = (
    (RULE_TYPE_DEVICE, 'Device'),
    (RULE_TYPE_ACTION, 'Action'),
)
