from django.conf import settings
from mongoengine import fields, DoesNotExist
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


class CitySerializer(mongoserializers.DocumentSerializer):
    class Meta:
        model = City
        fields = '__all__'


class OnlyCountrySerializer(mongoserializers.DocumentSerializer):
    class Meta:
        model = Country
        fields = ('id', 'country',)


class CountrySerializer(mongoserializers.DocumentSerializer):
    cities = CitySerializer(many=True)

    def validate(self, data):
        if 'country' in data:
            data['country'] = data['country'].capitalize()
        if 'cities' in data:
            data['cities'] = list(dict.fromkeys(map(lambda ct: ct.capitalize(), data['cities'])))
        return data

    def update(self, instance, raw_data):
        if not raw_data:
            return instance
        
        validated_data = self.validate(raw_data)
        if 'country' in validated_data:
            instance.update(country=validated_data['country'])

        if 'cities' in validated_data:
            for ct in instance.cities:
                ct.delete()
            instance.update(**{'cities': list(map(lambda ct: City(city=ct).save(), validated_data['cities']))})

        return instance.reload()

    class Meta:
        model = Country
        fields = ('id', 'country', 'cities')


class AmountFromGeneralReview(mongoserializers.DocumentSerializer):
    class Meta:
        model = GeneralReview
        fields = ('amount',)


class AddressSerializer(mongoserializers.EmbeddedDocumentSerializer):
    country = OnlyCountrySerializer(many=False)
    city = CitySerializer(many=False)

    class Meta:
        model = Address
        fields = ('country', 'city', 'street', 'coordinates')


class PlaceSerializer(mongoserializers.DocumentSerializer):
    address = AddressSerializer(many=False)

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

    def update(self, instance, raw_data):
        if not raw_data:
            return instance

        composite_fields = (
            (Category, 'categories'),
            (Cuisine, 'cuisines'),
            (AdditionalService, 'additional_services')
        )

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

        if 'address' in raw_data:
            country = raw_data['address']['country'] if 'country' in raw_data['address'] else None
            city = raw_data['address']['city'] if 'city' in raw_data['address'] else None
            street = raw_data['address']['street'] if 'street' in raw_data['address'] else None
            coordinates = raw_data['address']['coordinates'] if 'coordinates' in raw_data['address'] else None

            if country:
                try:
                    country = Country.objects.get(id=country)
                except DoesNotExist:
                    raise serializers.ValidationError('This country is not supported')

                if city:
                    try:
                        city = City.objects.get(id=city)
                        if city in country.cities:
                            if street:
                                if coordinates:
                                    instance.update(
                                        address__country=country,
                                        address__city=city,
                                        address__street=street,
                                        address__coordinates=coordinates
                                    )
                                else:
                                    raise serializers.ValidationError('Coordinates not provided')
                            else:
                                raise serializers.ValidationError('You must enter the street')
                        else:
                            raise serializers.ValidationError('This city is not in ' + country.country)
                    except DoesNotExist:
                        raise serializers.ValidationError('This city is not supported')
                else:
                    raise serializers.ValidationError('You must enter the city')
            else:
                raise serializers.ValidationError('You must enter the country')
                
        if 'address' in raw_data:
            raw_data.pop('address')
            
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
        depth = 3


class CardSerializer(mongoserializers.DocumentSerializer):
    general_review = AmountFromGeneralReview(many=False)
    address = AddressSerializer(many=False)

    class Meta:
            model = Place
            fields = ('title', 'cuisines', 'categories', 'operation_hours', 'general_review', 'address', 'rounded_rating')
            depth = 2


# class FavoritePlaceSerializer(mongoserializers.DocumentSerializer):
#     address = CitySerializer(many=False)

#     class Meta:
#         model = Place
#         fields = ('title', 'address',)


# class FavoriteSerializer(mongoserializers.DocumentSerializer):
#     place = FavoritePlaceSerializer(many=False)

#     class Meta:
#         model = Favorite
#         fields = ('place',)
