# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

from .constants import (STATUS_CHOICES, STATUS_INI, CHIP_STATUS_CHOICES, CHIP_STATUS_FREE,
                        LOG_TYPE_CHOICES, LOG_STATUS_CHOICES, ORIGIN_CHOICES, RULE_TYPE_CHOICES, RULE_TYPE_DEFAULT, RULE_FROM_TYPE_CHOICES,
                        RULE_TO_TYPE_CHOICES, RULE_STATUS_CHOICES, RULE_STATUS_OK)


class Device (models.Model):
    name = models.CharField(max_length=100)
    number = models.CharField(max_length=30)
    chip_id = models.CharField(max_length=100, blank=True, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=STATUS_INI)
    chip_status = models.CharField(max_length=10, choices=CHIP_STATUS_CHOICES, default=CHIP_STATUS_FREE)

    channel_i2c = models.CharField(max_length=10)
    last_connection = models.DateTimeField(null=True)
    enabled = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class LogDevice (models.Model):
    status = models.CharField(max_length=10, choices=LOG_STATUS_CHOICES)
    log_type = models.CharField(max_length=10, choices=LOG_TYPE_CHOICES)
    number = models.CharField(max_length=100, null=True)
    description = models.TextField(null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    device = models.ForeignKey(Device, on_delete=models.PROTECT,)


class LogAction (models.Model):
    status = models.CharField(max_length=10, choices=LOG_STATUS_CHOICES)
    origin = models.CharField(max_length=10, choices=ORIGIN_CHOICES)
    log_type = models.CharField(max_length=10, choices=LOG_TYPE_CHOICES)
    number = models.CharField(max_length=100, null=True)
    description = models.TextField(null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    device = models.ForeignKey(Device, on_delete=models.PROTECT,)


class Rule (models.Model):
    name = models.CharField(max_length=100)
    rule_type = models.CharField(max_length=10, choices=RULE_TYPE_CHOICES, default=RULE_TYPE_DEFAULT)
    from_type = models.CharField(max_length=10, choices=RULE_FROM_TYPE_CHOICES, null=True)
    from_number = models.CharField(max_length=255, null=True)
    to_type = models.CharField(max_length=10, choices=RULE_TO_TYPE_CHOICES, null=True)
    to_number = models.CharField(max_length=255, null=True)
    enabled = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    device = models.ForeignKey(Device, related_name='rules', on_delete=models.PROTECT,)


class RuleInstance (models.Model):
    status = models.CharField(max_length=10, choices=RULE_STATUS_CHOICES, default=RULE_STATUS_OK)
    description = models.TextField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    log = models.ForeignKey(LogDevice, on_delete=models.PROTECT,)
    rule = models.ForeignKey(Rule, on_delete=models.PROTECT,)
