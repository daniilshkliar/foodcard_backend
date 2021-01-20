import base64
import uuid
from django.conf import settings
from mongoengine import fields, DoesNotExist, errors
from rest_framework import serializers
from rest_framework_mongoengine import serializers as mongoserializers

from .models import *


class PlaceSerializer(mongoserializers.DocumentSerializer):
    main_photo = serializers.SerializerMethodField()

    def validate(self, data):
        if 'title' in data:
            data['title'] = data['title'].capitalize()

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
        print(validated_data)
        if 'main_photo' in validated_data:
            instance.main_photo.replace(validated_data.pop('main_photo'), content_type = 'image/jpeg')
            instance.save()

        #     photo_urls = []
        #     photos = validated_data.pop('photos')
        #     for photo in photos:
        #         file_name = f'{str(uuid.uuid4())}.jpg'
        #         file_location = f'{settings.MEDIA_ROOT}/{settings.PHOTO_URL}/{file_name}'
        #         uri = f'{settings.URI_ROOT}core/photo/get/{file_name}'
        #         with open(file_location, 'wb') as f:
        #             f.write(base64.b64decode(photo))
        #             photo_urls.append(uri)
        #     instance.update(photos=photo_urls)
        # delete all previous pictures

        if not validated_data:
            return instance

        instance.update(**validated_data)
        return instance.reload()
    
    def get_main_photo(self, obj):
        # handle array of images
        # return base64.b64encode(obj.main_photo.read())
        return f'{settings.URI_ROOT}core/main_photo/get/{obj.main_photo._id}/'

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


class FavoritePlaceSerializer(mongoserializers.DocumentSerializer):
    address = CitySerializer(many=False)

    class Meta:
        model = Place
        fields = ('title', 'address')


class FavoriteSerializer(mongoserializers.DocumentSerializer):
    places = FavoritePlaceSerializer(many=True)

    class Meta:
        model = Favorite
        fields = ('places',)