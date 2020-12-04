from mongoengine import fields
from rest_framework import serializers
from rest_framework_mongoengine import serializers as mongoserializers

from .models import *


class PlaceSerializer(mongoserializers.DocumentSerializer):
    class Meta:
        model = Place
        fields = '__all__'
        depth = 2


class CitySerializer(mongoserializers.EmbeddedDocumentSerializer):
    class Meta:
        model = Address
        fields = ('city',)


class FavoritePlaceSerializer(mongoserializers.DocumentSerializer):
    address = CitySerializer(many=False)

    class Meta:
        model = Place
        fields = ('title', 'address',)


class FavoriteSerializer(mongoserializers.DocumentSerializer):
    place = FavoritePlaceSerializer(many=False)

    class Meta:
        model = Favorite
        fields = ('place',)
