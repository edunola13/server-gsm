# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import json

from rest_framework import serializers

from apps.devices.models import Device, LogAction, LogDevice
from apps.devices.constants import LOG_ACTION_TYPE_SMS, LOG_ACTION_TYPE_RSMS


class DeviceSerializer(serializers.ModelSerializer):

    class Meta:
        model = Device
        fields = ('id', 'name', 'number', 'chip_id',
                  'status', 'chip_status', 'channel_i2c', 'index_sms'
                  'last_connection', 'enabled', 'created_at', 'updated_at')
        read_only_fields = ('id', 'chip_id', 'status',
                            'chip_status', 'index_sms',
                            'last_connection', 'created_at', 'updated_at')


class LogDeviceSerializer(serializers.ModelSerializer):
    device = DeviceSerializer()
    description = serializers.SerializerMethodField()

    class Meta:
        model = LogDevice
        fields = ('id', 'status', 'log_type',
                  'number', 'description',
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
        fields = ('id', 'log_type', 'number', 'description', 'device')

    def validate(self, data):
        log_type = None
        if self.instance:
            if self.instance.can_update():
                raise serializers.ValidationError("Invalid log action status")
            log_type = data['log_type'] if 'log_type' in data else self.instance.log_type
        else:
            log_type = data['log_type']

        if log_type == LOG_ACTION_TYPE_SMS:
            self.validate_description_send_sms(data['description'])
        if log_type == LOG_ACTION_TYPE_RSMS:
            self.validate_description_read_sms(data['description'])

        try:
            data['description'] = json.dumps(data['description'])
        except Exception:
            pass
        return data

    def validate_description_send_sms(self, description):
        if description is None or 'msg' not in description:
            raise serializers.ValidationError("Invalid description")

    def validate_description_read_sms(self, description):
        if description is None or 'index' not in description:
            raise serializers.ValidationError("Invalid description")
