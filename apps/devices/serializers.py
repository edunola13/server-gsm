# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import json

from rest_framework import serializers

from apps.devices.models import Device, LogAction, LogDevice


class DeviceSerializer(serializers.ModelSerializer):

    class Meta:
        model = Device
        fields = ('id', 'name', 'number', 'chip_id',
                  'status', 'chip_status', 'channel_i2c',
                  'last_connection', 'enabled', 'created_at', 'updated_at')
        read_only_fields = ('id', 'chip_id', 'status', 'chip_status',
                            'last_connection', 'created_at', 'updated_at')


class LogDeviceSerializer(serializers.ModelSerializer):
    device = DeviceSerializer()
    description = serializers.SerializerMethodField()
    response = serializers.SerializerMethodField()

    class Meta:
        model = LogDevice
        fields = ('id', 'status', 'log_type',
                  'number', 'description', 'response',
                  'device', 'created_at')

    def get_description(self, obj):
        return obj.get_description()


class LogActionSerializer(serializers.ModelSerializer):
    device = DeviceSerializer()
    description = serializers.SerializerMethodField()
    response = serializers.SerializerMethodField()

    class Meta:
        model = LogAction
        fields = ('id', 'status', 'origin', 'log_type',
                  'number', 'description',
                  'response', 'device', 'created_at')

    def get_description(self, obj):
        return obj.get_description()

    def get_response(self, obj):
        return obj.get_response()


class LogActionUpdateSerializer(serializers.ModelSerializer):
    description = serializers.DictField(child=serializers.CharField())

    class Meta:
        model = LogAction
        fields = ('id', 'status', 'origin', 'log_type',
                  'number', 'description', 'response',
                  'device', 'created_at')
        read_only_fields = ('id', 'origin', 'status', 'response', 'created_at')

    def validate(self, data):
        if self.instance in ['OK', 'CAN', 'PRO']:
            raise serializers.ValidationError("Invalid log action status")
        try:
            data['description'] = json.dumps(data['description'])
            #
            # VALIDAR SEGUN TIPO
            #
        except Exception:
            pass
        return data
