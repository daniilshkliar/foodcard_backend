import base64
import uuid
from django.conf import settings
from mongoengine import fields, DoesNotExist, errors
from rest_framework import serializers
from rest_framework_mongoengine import serializers as mongoserializers

from .models import *


class PlaceSerializer(mongoserializers.DocumentSerializer):
    def validate(self, data):
        if 'title' in data:
            data['title'] = data['title'].capitalize()

        main_category = data.get('main_category')
        categories = data.get('categories')
        if bool(main_category) != bool(categories):
            raise serializers.ValidationError('You must specify fields for both the main category and categories fields')
        if main_category and categories and not main_category in categories:
            raise serializers.ValidationError('The main category must be in the list of selected categories')

        main_cuisine = data.get('main_cuisine')
        cuisines = data.get('cuisines')
        if bool(main_cuisine) != bool(cuisines):
            raise serializers.ValidationError('You must specify fields for both the main cuisine and cuisines fields')
        if main_cuisine and cuisines and not main_cuisine in cuisines:
            raise serializers.ValidationError('The main cuisine must be in the list of selected cuisines')

        if 'operation_hours' in data:
            if len(data['operation_hours']) != 7:
                raise serializers.ValidationError('Operation hours must be quoted for all weekdays')
            for day in data['operation_hours']:
                if len(day) != 2:
                    raise serializers.ValidationError('Operation hours must be quoted for opening and closing')
        return data

    def create(self, validated_data):
        place = Place(**validated_data)
        review = GeneralReview()
        review.save()
        place.general_review = review
        place.save()
        return place

    def update(self, instance, validated_data):
        instagram = validated_data.get('instagram')
        if instagram and instagram == "https://www.instagram.com/":
            validated_data['instagram'] = None

        website = validated_data.get('website')
        if website and website == "http://www.none.com":
            validated_data['website'] = None            

        if main_photo := validated_data.get('main_photo'):
            if not main_photo in instance.photos:
                raise serializers.ValidationError('This main photo is not found in all photos')

        if not validated_data:
            return instance

        instance.update(**validated_data)
        return instance.reload()

    class Meta:
        model = Place
        fields = '__all__'
        depth = 2


class AmountAndRoundedRatingFromGeneralReview(mongoserializers.DocumentSerializer):
    class Meta:
        model = GeneralReview
        fields = ('amount', 'rounded_rating')


class CardSerializer(mongoserializers.DocumentSerializer):
    general_review = AmountAndRoundedRatingFromGeneralReview(many=False)

    class Meta:
        model = Place
        fields = ('title', 'main_cuisine', 'main_category', 'operation_hours', 'general_review', 'address', 'main_photo')


class CitySerializer(mongoserializers.DocumentSerializer):
    class Meta:
        model = Address
        fields = ('city',)


class CountryCityStreetSerializer(mongoserializers.DocumentSerializer):
    class Meta:
        model = Address
        fields = ('country', 'city', 'street')


class FavoritePlaceSerializer(mongoserializers.DocumentSerializer):
    address = CitySerializer(many=False)

    class Meta:
        model = Place
        fields = ('id', 'title', 'address')


class FavoriteSerializer(mongoserializers.DocumentSerializer):
    places = FavoritePlaceSerializer(many=True)

    class Meta:
        model = Favorite
        fields = ('places',)


class PlacesForControlPanelSerializer(mongoserializers.DocumentSerializer):
    address = CountryCityStreetSerializer(many=False)

    def validate(self, data):
        pass

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass

    class Meta:
        model = Place
        fields = ('id', 'title', 'address', 'is_active')