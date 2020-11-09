from rest_framework import serializers

from django.contrib.auth.models import User

from .models import *


class UserSerializer(serializers.Serializer):

    email = serializers.EmailField(write_only=True)
    first_name = serializers.CharField(write_only=True)
    last_name = serializers.CharField(write_only=True)
    password1 = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)

    def validate(self, data):
        if data['password1'] != data['password2']:
            raise serializers.ValidationError('Passwords must match')
        if User.objects.filter(email=data['email']).exists():
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