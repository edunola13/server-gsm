# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

from apps.devices.constants import ORIGIN_CHOICES
from .constants import *

from apps.devices.models import Device, LogDevice


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
