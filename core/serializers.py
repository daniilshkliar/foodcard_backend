from rest_framework import serializers
from rest_framework_mongoengine import serializers as mongoserializers

from .models import *


class PlaceSerializer(mongoserializers.DocumentSerializer):

    class Meta:
        model = Place
        fields = '__all__'


class CategorySerializer(mongoserializers.DocumentSerializer):
    
    class Meta:
        model = Category
        fields = '__all__'