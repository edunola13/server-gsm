# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import json

from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey

from .constants import *
from .strategy import STRATEGY_CLASS_DEV, STRATEGY_CLASS_ACT

from apps.devices.models import Device


class Rule (models.Model):
    name = models.CharField(max_length=100)
    strategy = models.CharField(
        max_length=10, choices=RULE_STRATEGY_CHOICES)
    rule_type = models.CharField(
        max_length=10,
        choices=RULE_TYPE_CHOICES)
    # Aca ponemos toda la data que necesita (buscar y enviar)
    description = models.TextField(null=True)
    enabled = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    device = models.ForeignKey(
        Device,
        related_name='rules',
        on_delete=models.PROTECT,)  # Puede no tener device

    def check_rule(self, event):
        strategy = self._get_strategy()
        strategy.check_rule(event)

    def _get_strategy(self):
        klass = STRATEGY_CLASS_DEV[self.strategy] if RULE_TYPE_DEVICE == self.rule_type else STRATEGY_CLASS_ACT[self.strategy]
        return klass(self)

    def get_description(self):
        try:
            return json.loads(self.description)
        except Exception:
            return None


class RuleInstance (models.Model):
    description = models.TextField(null=True)  # Info de ejecucion
    created_at = models.DateTimeField(auto_now_add=True)

    rule = models.ForeignKey(Rule, on_delete=models.PROTECT,)

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True)
    object_id = models.PositiveIntegerField(null=True)
    thrower = GenericForeignKey('content_type', 'object_id')

    def get_description(self):
        try:
            return json.loads(self.description)
        except Exception:
            return None
