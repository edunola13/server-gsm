# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from rest_framework import viewsets, status
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin
from rest_framework.viewsets import GenericViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import serializers

from rest_framework.permissions import IsAdminUser
from server.exceptions import ConflictError

from apps.devices.models import (Device, LogDevice, LogAction)
from apps.rules.models import (Rule, RuleInstance)

from apps.devices.serializers import (
    DeviceSerializer, LogDeviceSerializer,
    LogActionSerializer, LogActionUpdateSerializer)
from apps.rules.serializers import (
    RuleSerializer, RuleInstanceSerializer)
from apps.devices.constants import ORIGIN_API

from apps.devices.tasks import execute_action


class DeviceViewSet(viewsets.ModelViewSet):
    permission_classes = ()  # (IsAdminUser,)

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
    permission_classes = ()  # (IsAdminUser,)

    queryset = LogDevice.objects.all()
    serializer_class = LogDeviceSerializer

    __basic_fields = ('number',)
    filter_fields = __basic_fields + ('status', 'log_type', 'created_at')
    search_fields = __basic_fields
    ordering_fields = __basic_fields + ('created_at',)
    ordering = 'created_at'

    @action(methods=['put'], detail=True)
    def change_status(self, request, pk=None):
        log = self.get_object()
        if not log.can_update():
            err = 'Invalid log device status'
            raise ConflictError(detail=err)

        status = request.data.get('status', None)
        if status not in ['INI', 'CAN']:
            raise serializers.ValidationError({'status': "Invalid status"})

        log.status = status
        log.save()

        serializer = LogDeviceSerializer(log)
        return Response(serializer.data)


class LogActionViewSet(viewsets.ModelViewSet):
    permission_classes = ()  # (IsAdminUser,)

    queryset = LogAction.objects.all()
    serializer_class = LogActionSerializer

    __basic_fields = ('number',)
    filter_fields = __basic_fields + ('origin', 'status', 'log_type', 'created_at')
    search_fields = __basic_fields
    ordering_fields = __basic_fields
    ordering = 'created_at'

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return LogActionUpdateSerializer
        return self.serializer_class

    def perform_create(self, serializer):
        serializer.save(origin=ORIGIN_API)
        execute_action.apply_async([serializer.instance.id])

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        serializer = LogActionSerializer(serializer.instance)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data,
                        status=status.HTTP_201_CREATED,
                        headers=headers)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', True)
        instance = self.get_object()
        serializer = self.get_serializer(instance,
                                         data=request.data,
                                         partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        serializer = LogActionSerializer(serializer.instance)
        return Response(serializer.data)

    @action(methods=['put'], detail=True)
    def change_status(self, request, pk=None):
        action = self.get_object()
        if not action.can_update():
            err = 'Invalid log action status'
            raise ConflictError(detail=err)

        status = request.data.get('status', None)
        if status not in ['INI', 'CAN']:
            raise serializers.ValidationError({'status': "Invalid status"})

        action.status = status
        action.save()

        serializer = LogActionSerializer(action)
        return Response(serializer.data)
