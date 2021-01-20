import json
from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_mongoengine import serializers as mongoserializers
from mongoengine import fields, DoesNotExist, errors

from .models import *
from core.models import *


class UserSerializer(serializers.ModelSerializer):
    manager_of = serializers.SerializerMethodField()

    def get_manager_of(self, obj):
        manager_of = Manager.objects(user=obj.id).only('places').first()
        if manager_of:
            data = json.loads(manager_of.to_json())
            return data.get('places', [])
        else:
            return []

    class Meta:
        model = User
        fields = ('id', 'email', 'first_name', 'last_name', 'is_superuser', 'manager_of')


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(write_only=True)
    password = serializers.CharField(write_only=True)
    tokens = serializers.SerializerMethodField()

    def validate(self, data):
        user = User.objects.filter(email=data['email']).first()
        if not user or not user.check_password(data['password']):
            raise serializers.ValidationError('No active account found with the given credentials')
        return data

    def get_tokens(self, obj):
        user = User.objects.get(email=obj['email'])
        return RefreshToken.for_user(user)


class SignupSerializer(serializers.Serializer):
    email = serializers.EmailField(write_only=True)
    first_name = serializers.CharField(write_only=True)
    last_name = serializers.CharField(write_only=True)
    password1 = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)

    def validate(self, data):
        if data['password1'] != data['password2']:
            raise serializers.ValidationError('Passwords must match')
        if User.objects.filter(email=data['email']).first():
            raise serializers.ValidationError('An account with this email already exists')
        return data

    def create(self, validated_data):
        data = {
            key: value for key, value in validated_data.items()
            if key not in ('password1', 'password2')
        }
        data['password'] = validated_data['password1']
        data['username'] = validated_data['email']
        return User.objects.create_user(**data)