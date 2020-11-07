from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
import re

from .models import *


class Signup(serializers.ModelSerializer):

    password1 = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)
    token = serializers.SerializerMethodField()

    def get_token(self, user):
        refresh = RefreshToken.for_user(user)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }

    def validate(self, data):
        if data['password1'] != data['password2']:
            raise serializers.ValidationError('Passwords must match')
        if not data['email']:
            raise serializers.ValidationError('Email is required')
        if User.objects.filter(email=data['email']).exists():
            raise serializers.ValidationError('Email addresses must be unique')
        if not data['first_name']:
            raise serializers.ValidationError('First name is required')
        if re.search(r"^[a-zA-Z]+$", data['first_name']):
            raise serializers.ValidationError('First name must be alphabetic')
        if not data['last_name']:
            raise serializers.ValidationError('Last name is required')
        if re.search(r"^[a-zA-Z]+$", data['last_name']):
            raise serializers.ValidationError('Last name must be alphabetic')
        return data

    def create(self, validated_data):
        data = {
            key: value for key, value in validated_data.items()
            if key not in ('password1', 'password2')
        }
        data['password'] = validated_data['password1']
        data['username'] = validated_data['email']
        return User.objects.create_user(**data)
    
    class Meta:
        model = User
        fields = ('id', 'email', 'first_name', 'last_name', 'password1', 'password2', 'token')