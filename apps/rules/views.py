# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from rest_framework import viewsets
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin
from rest_framework.viewsets import GenericViewSet

from rest_framework.permissions import IsAdminUser

from apps.rules.models import (Rule, RuleInstance)

from apps.rules.serializers import (
    RuleSerializer, RuleInstanceSerializer)


class RuleViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAdminUser,)

    queryset = Rule.objects.all()
    serializer_class = RuleSerializer

    __basic_fields = ('name',)
    filter_fields = __basic_fields + ('strategy' 'rule_type', 'enabled', 'device', 'date_created')
    search_fields = __basic_fields
    ordering_fields = __basic_fields + ('strategy', 'date_created')
    ordering = 'date_created'


class RuleInstanceViewSet(ListModelMixin, RetrieveModelMixin, GenericViewSet):
    permission_classes = (IsAdminUser,)

    queryset = RuleInstance.objects.all()
    serializer_class = RuleInstanceSerializer

    filter_fields = ('rule', 'rule__rule_type', 'date_created')
    ordering_fields = ('rule__rule_type', 'date_created')
    ordering = 'date_created'
