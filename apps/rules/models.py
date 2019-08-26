# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

from .constants import *
from .strategy import STRATEGY_CLASS

# from apps.devices.models import Device, LogDevice


class Rule (models.Model):
    name = models.CharField(max_length=100)
    strategy = models.CharField(
        max_length=10, choices=RULE_STRATEGY_CHOICES)
    rule_type = models.CharField(
        max_length=10,
        choices=RULE_TYPE_CHOICES, default=RULE_TYPE_DEVICE)

    # NO MASSSS
    # from_type = models.CharField(
    #     max_length=10,
    #     choices=RULE_FROM_TYPE_CHOICES, null=True)
    # from_number = models.CharField(max_length=255, null=True)
    # to_type = models.CharField(
    #     max_length=10,
    #     choices=RULE_TO_TYPE_CHOICES, null=True)
    # to_number = models.CharField(max_length=255, null=True)

    # Aca ponemos toda la data que necesita (buscar y enviar)
    description = models.TextField(null=True)
    enabled = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    device = models.ForeignKey(
        Device,
        related_name='rules',
        on_delete=models.PROTECT,)  # Puede no tener device

    def check_rule(self, from_date):
        strategy = self.__get_strategy()
        strategy.check_rule(from_date)

    def __get_strategy():
        klass = STRATEGY_CLASS[self.strategy]
        return klass(self)


class RuleInstance (models.Model):
    description = models.TextField(null=True)  # Info de ejecucion
    created_at = models.DateTimeField(auto_now_add=True)

    rule = models.ForeignKey(Rule, on_delete=models.PROTECT,)
