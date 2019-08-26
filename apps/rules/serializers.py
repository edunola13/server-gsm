# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from rest_framework import serializers

from apps.rules.models import Rule, RuleInstance
from apps.devices.models import Device

from apps.devices.serializers import DeviceSerializer


class RuleSerializer(serializers.ModelSerializer):
    device = DeviceSerializer(write_only=True)
    device_id = employee_id = serializers.PrimaryKeyRelatedField(
        source='device', queryset=Device.objects.all(), write_only=True
    )

    class Meta:
        model = Rule
        fields = ('id', 'name', 'strategy', 'rule_type', 'description'
                  'enabled', 'device', 'device_id', 'created_at', 'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at')

    def validate(self, data):
        #
        # CHECK QUE EN DESCRIPTION ESTE LO QUE PIDA LA STRATEGIA QUE CORRESPONDA
        #
        if False:
            raise serializers.ValidationError("Invalid description")

        return data


class RuleInstanceSerializer(serializers.ModelSerializer):

    class Meta:
        model = RuleInstance
        fields = ('id', 'status', 'description', 'rule', 'created_at')
