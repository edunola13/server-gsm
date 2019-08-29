# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import json

from rest_framework import serializers

from apps.rules.models import Rule, RuleInstance
from apps.devices.models import Device

from apps.devices.serializers import DeviceSerializer

from apps.rules.constants import RULE_TYPE_DEVICE
from apps.rules.strategy import STRATEGY_CLASS_ACT, STRATEGY_CLASS_DEV


class RuleSerializer(serializers.ModelSerializer):
    device = DeviceSerializer(read_only=True)
    description = serializers.SerializerMethodField()

    class Meta:
        model = Rule
        fields = ('id', 'name', 'strategy', 'rule_type', 'description',
                  'enabled', 'device', 'created_at', 'updated_at')

    def get_description(self, obj):
        return obj.get_description()


class RuleUpdateSerializer(serializers.ModelSerializer):
    device_id = serializers.PrimaryKeyRelatedField(
        source='device', queryset=Device.objects.all()
    )
    description = serializers.DictField(child=serializers.CharField())

    class Meta:
        model = Rule
        fields = ('name', 'strategy', 'rule_type', 'description',
                  'enabled', 'device_id',)

    def validate(self, data):
        rule_type = data['rule_type'] if 'rule_type' in data else self.instance.rule_type
        strategy = data['strategy'] if 'strategy' in data else self.instance.strategy
        STRATEGY_CLASSES = STRATEGY_CLASS_DEV if rule_type == RULE_TYPE_DEVICE else STRATEGY_CLASS_ACT
        if strategy not in STRATEGY_CLASSES:
            raise serializers.ValidationError("Invalid strategy")

        klass = STRATEGY_CLASSES[strategy]
        description = data['description'] if 'description' in data else self.instance.description
        if not klass.is_valid_description(description):
            raise serializers.ValidationError("Invalid description")

        try:
            data['description'] = json.dumps(data['description'])
        except Exception:
            pass

        return data


class RuleInstanceSerializer(serializers.ModelSerializer):
    description = serializers.SerializerMethodField()

    class Meta:
        model = RuleInstance
        fields = ('id', 'description', 'rule', 'created_at')

    def get_description(self, obj):
        return obj.get_description()
