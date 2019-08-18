# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from rest_framework import serializers

from apps.devices.models import Device, LogAction, LogDevice, Rule, RuleInstance


class DeviceSerializer(serializers.ModelSerializer):

    class Meta:
        model = Device
        fields = ('id', 'name', 'number', 'chip_id' 'status', 'chip_status',
                  'channel_i2c', 'last_connection', 'enabled', 'created_at', 'updated_at')
        read_only_fields = ('id', 'chip_id', 'status', 'chip_status', 'last_connection',
                            'created_at', 'updated_at')


class LogDeviceSerializer(serializers.ModelSerializer):
    device = DeviceSerializer()

    class Meta:
        model = LogDevice
        fields = ('id', 'status', 'log_type', 'number', 'description', 'device', 'created_at')


class LogActionSerializer(serializers.ModelSerializer):
    device = DeviceSerializer()

    class Meta:
        model = LogAction
        fields = ('id', 'status', 'origin', 'log_type', 'number', 'description', 'device', 'created_at')
        read_only_fields = ('id', 'status', 'created_at')


class RuleSerializer(serializers.ModelSerializer):
    device = DeviceSerializer()

    class Meta:
        model = Rule
        fields = ('id', 'name', 'rule_type', 'from_type', 'from_number', 'to_type',
                  'to_number', 'enabled', 'device', 'created_at', 'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at')


class RuleInstanceSerializer(serializers.ModelSerializer):
    device = DeviceSerializer()
    log = LogDeviceSerializer()

    class Meta:
        model = RuleInstance
        fields = ('id', 'status', 'description', 'device', 'log', 'created_at')
