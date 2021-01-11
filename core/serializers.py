from django.conf import settings
from mongoengine import fields
from rest_framework import serializers
from rest_framework_mongoengine import serializers as mongoserializers
import base64
import uuid

from .models import *


class CategorySerializer(mongoserializers.DocumentSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class CuisineSerializer(mongoserializers.DocumentSerializer):
    class Meta:
        model = Cuisine
        fields = '__all__'


class AdditionalServiceSerializer(mongoserializers.DocumentSerializer):
    class Meta:
        model = AdditionalService
        fields = '__all__'


class CitySerializer(mongoserializers.EmbeddedDocumentSerializer):
    class Meta:
        model = Address
        fields = ('city',)


class PlaceSerializer(mongoserializers.DocumentSerializer):
    def validate(self, data):
        if 'title' in data:
            data['title'] = data['title'].capitalize()
        if 'address' in data:
            if 'country' in data['address']:
                data['address']['country'] = data['address']['country'].capitalize()
            if 'city' in data['address']:
                data['address']['city'] = data['address']['city'].capitalize()

        if 'operation_hours' in data:
            if len(data['operation_hours']) != 7:
                raise serializers.ValidationError('Operation hours must be quoted for all weekdays')
            for day in data['operation_hours']:
                if len(day) != 2:
                    raise serializers.ValidationError('Operation hours must be quoted for opening and closing')
        return data

    def update(self, instance, raw_data):
        if not raw_data:
            return instance

        if 'photos' in raw_data:
            photo_urls = []
            photos = raw_data.pop('photos')
            for photo in photos:
                file_name = f'{str(uuid.uuid4())}.jpg'
                file_location = f'{settings.MEDIA_ROOT}/{settings.PHOTO_URL}/{file_name}'
                uri = f'{settings.URI_ROOT}core/photo/get/{file_name}'
                with open(file_location, 'wb') as f:
                    f.write(base64.b64decode(photo))
                    photo_urls.append(uri)
            instance.update(photos=photo_urls)

        composite_fields = (
            (Category, 'categories'),
            (Cuisine, 'cuisines'),
            (AdditionalService, 'additional_services')
        )
        
        validated_data = self.validate(raw_data)
        data = {
            key: value for key, value in validated_data.items()
            if key not in (fields[1] for fields in composite_fields)
        }
        if data:
            instance.update(**data)

        for model, field in composite_fields:
            if field in validated_data:
                instance.update(**{field: list(map(lambda id: model.objects.get(id=id), validated_data[field]))})

        return instance.reload()
        
    class Meta:
        model = Place
        fields = '__all__'
        depth = 2


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
