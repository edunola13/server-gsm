# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from rest_framework import serializers
from django.contrib.auth.models import User, Group


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ('id', 'name',)


class UserBaseSerializer(serializers.ModelSerializer):
    groups = GroupSerializer(many=True, read_only=True)

    def create(self, validated_data):
        user = super(UserBaseSerializer, self).create(validated_data)
        if 'password' in validated_data:
            user.set_password(validated_data['password'])
            user.save()
        return user

    def update(self, instance, validated_data):
        user = super(UserBaseSerializer, self).update(instance, validated_data)
        if 'password' in validated_data:
            user.set_password(validated_data['password'])
            user.save()
        return user


class UserSerializer(UserBaseSerializer):
    groups_id = serializers.PrimaryKeyRelatedField(source='groups', queryset=Group.objects.all(), write_only=True, many=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'is_staff', 'is_active', 'groups', 'groups_id', 'password')
        extra_kwargs = {
            'password': {'write_only': True},
        }


class UserNoStaffSerializer(UserBaseSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'is_staff', 'is_active' , 'groups', 'password')
        extra_kwargs = {
            'password': {'write_only': True},
            'is_staff': {'read_only': True},
            'is_active': {'read_only': True},
        }

#SIMPLE SERIALIZER
class UserSimpleSerializer(UserBaseSerializer):

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'is_staff')
