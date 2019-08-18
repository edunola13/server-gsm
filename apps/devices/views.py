# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from rest_framework import viewsets, status
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin
from rest_framework.viewsets import GenericViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import serializers

from rest_framework.permissions import IsAdminUser

from apps.devices.models import Device, LogDevice, LogAction, Rule, RuleInstance
from apps.devices.serializers import (DeviceSerializer, LogDeviceSerializer, LogActionSerializer,
                                      RuleSerializer, RuleInstanceSerializer)
from apps.devices.constants import ORIGIN_API


class DeviceViewSet(viewsets.ModelViewSet):
    permission_classes = ()

    queryset = Device.objects.all()
    serializer_class = DeviceSerializer

    __basic_fields = ('name', 'number')
    filter_fields = __basic_fields + ('last_connection', 'enabled', 'status', 'chip_status')
    search_fields = __basic_fields
    ordering_fields = __basic_fields
    ordering = 'name'

    @action(methods=['get'], detail=True)
    def logs_device(self, request, pk=None):
        logs = LogDevice.objects.filter(device__id=pk)

        page = self.paginate_queryset(logs)
        serializer = LogDeviceSerializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(methods=['get'], detail=True)
    def logs_action(self, request, pk=None):
        logs = LogAction.objects.filter(device__id=pk)

        page = self.paginate_queryset(logs)
        serializer = LogActionSerializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(methods=['get'], detail=True)
    def rules(self, request, pk=None):
        rules = Rule.objects.filter(device__id=pk)

        page = self.paginate_queryset(rules)
        serializer = RuleSerializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(methods=['get'], detail=True)
    def rules_instances(self, request, pk=None):
        instances = RuleInstance.objects.filter(rule__device__id=pk)

        page = self.paginate_queryset(instances)
        serializer = RuleInstanceSerializer(page, many=True)
        return self.get_paginated_response(serializer.data)


class LogDeviceViewSet(ListModelMixin, RetrieveModelMixin, GenericViewSet):
    permission_classes = (IsAdminUser,)

    queryset = LogDevice.objects.all()
    serializer_class = LogDeviceSerializer

    __basic_fields = ('number',)
    filter_fields = __basic_fields + ('status', 'log_type', 'date_created')
    search_fields = __basic_fields
    ordering_fields = __basic_fields
    ordering = 'date_created'


class LogActionViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAdminUser,)

    queryset = LogAction.objects.all()
    serializer_class = LogActionSerializer

    __basic_fields = ('number',)
    filter_fields = __basic_fields + ('origin', 'status', 'log_type', 'date_created')
    search_fields = __basic_fields
    ordering_fields = __basic_fields
    ordering = 'date_created'

    def perform_create(self, serializer):
        serializer.save(origin=ORIGIN_API)

    def perform_update(self, serializer):
        if serializer.instance.origin != ORIGIN_API:
            raise serializers.ValidationError({'error': 'No se puede editar una accion que no es de origen API'})
        serializer.save()


class RuleViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAdminUser,)

    queryset = Rule.objects.all()
    serializer_class = RuleSerializer

    __basic_fields = ('name',)
    filter_fields = __basic_fields + ('rule_type', 'from_type', 'to_type', 'from_number', 'to_number', 'enabled', 'date_created')
    search_fields = __basic_fields
    ordering_fields = __basic_fields
    ordering = 'date_created'


class RuleInstanceViewSet(ListModelMixin, RetrieveModelMixin, GenericViewSet):
    permission_classes = (IsAdminUser,)

    queryset = RuleInstance.objects.all()
    serializer_class = RuleInstanceSerializer

    __basic_fields = ()
    filter_fields = __basic_fields + ('status', 'log', 'rule', 'rule_type', 'log_type', 'date_created')
    ordering_fields = __basic_fields
    ordering = 'date_created'
