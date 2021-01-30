import base64
import uuid
from django.conf import settings
from mongoengine import fields, DoesNotExist, errors
from rest_framework import serializers
from rest_framework_mongoengine import serializers as mongoserializers
from timezonefinder import TimezoneFinder

from .models import *


class ImageSerializer(mongoserializers.DocumentSerializer):
    class Meta:
        model = Image
        fields = '__all__'


class ImageThumbnailSerializer(mongoserializers.DocumentSerializer):
    class Meta:
        model = Image
        fields = ('id', 'thumbnail_uri',)


class PlaceSerializer(mongoserializers.DocumentSerializer):
    main_photo = ImageThumbnailSerializer(many=False)
    photos = ImageSerializer(many=True)

    def validate(self, data):
        if 'title' in data:
            data['title'] = data['title'].capitalize()

        for main_field_title, field_title in (('main_category', 'categories'), ('main_cuisine', 'cuisines')):
            main_field = data.get(main_field_title)
            field = data.get(field_title)
            if bool(main_field) != bool(field):
                raise serializers.ValidationError(f'You must specify fields for both the {main_field_title} and {field_title} fields')
            if main_field and field and not main_field in field:
                raise serializers.ValidationError(f'The {main_field_title} must be in the list of selected {field_title}')

        if 'opening_hours' in data:
            if len(data['opening_hours']) != 7:
                raise serializers.ValidationError('opening hours must be quoted for all weekdays')
            for day in data['opening_hours']:
                if len(day) != 2:
                    raise serializers.ValidationError('opening hours must be quoted for opening and closing')
        return data

    def create(self, validated_data):
        place = Place(**validated_data)
        review = GeneralReview()
        review.save()
        place.general_review = review
        
        try:
            latitude, longitude = validated_data.get('address').get('coordinates')
            if latitude and longitude:
                place.timezone = TimezoneFinder().timezone_at(lat=latitude, lng=longitude)
        except AttributeError:
            pass

        place.save()
        return place

    def update(self, instance, validated_data):
        instagram = validated_data.get('instagram')
        if instagram and instagram == "https://www.instagram.com/":
            validated_data['instagram'] = None

        website = validated_data.get('website')
        if website and website == "http://www.none.com":
            validated_data['website'] = None

        if not validated_data:
            return instance

        try:
            latitude, longitude = validated_data.get('address').get('coordinates')
            if latitude and longitude:
                validated_data['timezone'] = TimezoneFinder().timezone_at(lat=latitude, lng=longitude)
        except AttributeError:
            pass

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
    main_photo = ImageThumbnailSerializer(many=False)

    class Meta:
        model = Place
        fields = ('title', 'main_cuisine', 'main_category', 'opening_hours', 'general_review', 'address', 'main_photo', 'timezone')


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