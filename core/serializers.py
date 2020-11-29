from rest_framework import serializers
from rest_framework_mongoengine import serializers as mongoserializers
from mongoengine import fields

from .models import *


class PlaceSerializer(mongoserializers.DocumentSerializer):

    class Meta:
        model = Place
        fields = '__all__'


class FavoriteSerializer(mongoserializers.DocumentSerializer):

    class Meta:
        model = Favorite
        fields = '__all__'