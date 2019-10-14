# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from rest_framework import viewsets, status
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin
from rest_framework.viewsets import GenericViewSet
from rest_framework.response import Response

from rest_framework.permissions import IsAdminUser

from apps.rules.models import (Rule, RuleInstance)

from apps.rules.serializers import (
    RuleSerializer, RuleUpdateSerializer, RuleInstanceSerializer)


class RuleViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAdminUser,)

    queryset = Rule.objects.all()
    serializer_class = RuleSerializer

    __basic_fields = ('name',)
    filter_fields = __basic_fields + ('strategy', 'rule_type', 'enabled', 'device', 'created_at')
    search_fields = __basic_fields
    ordering_fields = __basic_fields + ('strategy', 'created_at')
    ordering = 'name'

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return RuleUpdateSerializer
        return self.serializer_class

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        serializer = RuleSerializer(serializer.instance)
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

        serializer = RuleSerializer(serializer.instance)
        return Response(serializer.data)


class RuleInstanceViewSet(ListModelMixin, RetrieveModelMixin, GenericViewSet):
    permission_classes = (IsAdminUser,)

    queryset = RuleInstance.objects.all()
    serializer_class = RuleInstanceSerializer

    filter_fields = ('is_ok', 'rule', 'rule__rule_type', 'created_at')
    ordering_fields = ('rule__rule_type', 'created_at')
    ordering = '-created_at'
