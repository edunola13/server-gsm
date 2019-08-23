# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from rest_framework import serializers

from apps.rules.models import Rule, RuleInstance
from apps.devices.models import Device

from apps.devices.serializers import DeviceSerializer, LogDeviceSerializer


class RuleSerializer(serializers.ModelSerializer):
    device = DeviceSerializer(write_only=True)
    device_id = employee_id = serializers.PrimaryKeyRelatedField(
        source='device', queryset=Device.objects.all(), write_only=True
    )

    class Meta:
        model = Rule
        fields = ('id', 'name', 'rule_type', 'from_type',
                  'from_number', 'to_type', 'to_number',
                  'enabled', 'device', 'device_id', 'created_at', 'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at')


class RuleInstanceSerializer(serializers.ModelSerializer):
    device = DeviceSerializer()
    log = LogDeviceSerializer()

    class Meta:
        model = RuleInstance
        fields = ('id', 'status', 'description', 'device', 'log', 'created_at')
