# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from apps.users.permissions import IsAdminOrSameUser

from django.contrib.auth.models import User, Group
from apps.users.serializers import UserSerializer, UserNoStaffSerializer, GroupSerializer


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAdminOrSameUser, )
    __basic_fields = ('username',)
    filter_fields = __basic_fields + ('groups', 'is_staff')
    search_fields = __basic_fields
    ordering_fields = __basic_fields
    ordering = 'username'

    def get_serializer_class(self):
        if not self.request.user.is_staff:
            return UserNoStaffSerializer
        return self.serializer_class


class CurrentUserView(APIView):
    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)


class GroupViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = (IsAdminUser, )
    __basic_fields = ('name')
    search_fields = __basic_fields
    ordering_fields = __basic_fields
    ordering = 'name'
