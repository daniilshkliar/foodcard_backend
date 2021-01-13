import json
import mongoengine
from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from backend.permissions import IsAdminUserOrReadOnly
from rest_framework_mongoengine.viewsets import ModelViewSet as MongoModelViewSet

from .models import *   
from .serializers import *


class CountryViewSet(MongoModelViewSet):
    queryset = Country.objects.all()
    serializer_class = CountrySerializer
    permission_classes = [IsAdminUserOrReadOnly,]

    def list(self, request):
        serializer = self.get_serializer(self.queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def retrieve(self, request, pk=None):
        try:
            country = self.queryset.get(id=pk)
            serializer = self.get_serializer(country)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except mongoengine.DoesNotExist:
            return Response({'message': 'This country is not supported'}, status=status.HTTP_404_NOT_FOUND)

    def create(self, request):
        try:
            country = Country(country=request.data['country'].capitalize())
            if 'cities' in request.data:
                for ct in request.data['cities']:
                    city = City(city=ct)
                    city.save()
                    country.cities.append(city)
            country.save()
            serializer = self.get_serializer(country)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except mongoengine.errors.NotUniqueError:
            return Response({'message': 'This country already exists'}, status=status.HTTP_400_BAD_REQUEST)
        except mongoengine.errors.ValidationError as e:
            return Response({'error': 'Validation error', 'message': e.errors}, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        try:
            country = self.queryset.get(id=pk)
            serializer = self.get_serializer(country)
            serializer.update(country, request.data)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except mongoengine.DoesNotExist:
            return Response({'message': 'This country is not supported'}, status=status.HTTP_404_NOT_FOUND)
        except mongoengine.errors.NotUniqueError:
            return Response({'message': 'This country already exists'}, status=status.HTTP_400_BAD_REQUEST)
        except mongoengine.errors.ValidationError as e:
            return Response({'error': 'Validation error', 'message': e.errors}, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        try:
            country = self.queryset.get(id=pk)
            for ct in country.cities:
                ct.delete()
            country.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except mongoengine.DoesNotExist:
            return Response({'message': 'This country is not supported'}, status=status.HTTP_404_NOT_FOUND)


class CityViewSet(MongoModelViewSet):
    queryset = City.objects.all()
    serializer_class = CitySerializer
    permission_classes = [IsAdminUserOrReadOnly,]

    def list(self, request):
        serializer = self.get_serializer(self.queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request):
        try:
            country = request.data['country'] if 'country' in request.data else None
            city = request.data['city'] if 'city' in request.data else None

            if country:
                try:
                    country = Country.objects.get(id=country)
                except DoesNotExist:
                    return Response({'message': 'This country is not supported'}, status=status.HTTP_404_NOT_FOUND)
                    
                if city:
                    cities = City.objects(city=city)
                    for cty in cities:
                        if cty in country.cities:
                            return Response({'message': cty.city + ' already exists in ' + country.country}, status=status.HTTP_400_BAD_REQUEST)
                    city = City(city=city)
                    city.save()
                    country.cities.append(city)
                    country.save()
                    serializer = self.get_serializer(city)
                    return Response(serializer.data, status=status.HTTP_201_CREATED)
                else:
                    return Response({'message': 'You must enter the city'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({'message': 'You must enter the country'}, status=status.HTTP_400_BAD_REQUEST)
        except mongoengine.errors.ValidationError as e:
            return Response({'error': 'Validation error', 'message': e.errors}, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        pass

    def destroy(self, request):
        try:
            country = Country.objects.get(id=request.data['country'])
            city = City.objects.get(id=request.data['city'])
            if city in country.cities:
                city.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            else:
                return Response({'message': 'This city is not in ' + country.country}, status=status.HTTP_400_BAD_REQUEST)
        except mongoengine.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)


class DocumentListViewSet(MongoModelViewSet):
    permission_classes = [IsAdminUserOrReadOnly,]

    def list(self, request):
        serializer = self.get_serializer(self.queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def create(self, request):
        try:
            obj = self.model(title=request.data['title'].capitalize())
            obj.save()
            serializer = self.get_serializer(obj)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except mongoengine.errors.NotUniqueError:
            return Response({'message': 'This ' + self.desrciption + ' already exists'}, status=status.HTTP_400_BAD_REQUEST)
        except mongoengine.errors.ValidationError as e:
            return Response({'error': 'Validation error', 'message': e.errors}, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        pass

    def destroy(self, request, pk=None):
        try:
            obj = self.queryset.get(id=pk)
            obj.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except mongoengine.DoesNotExist:
            return Response({'message': 'This ' + self.desrciption + ' does not exist'}, status=status.HTTP_404_NOT_FOUND)


class CategoryViewSet(DocumentListViewSet):
    model = Category
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    desrciption = 'category'


class CuisineViewSet(DocumentListViewSet):
    model = Cuisine
    queryset = Cuisine.objects.all()
    serializer_class = CuisineSerializer
    desrciption = 'cuisine'


class AdditionalServiceViewSet(DocumentListViewSet):
    model = AdditionalService
    queryset = AdditionalService.objects.all()
    serializer_class = AdditionalServiceSerializer
    desrciption = 'additional service'


class PlaceViewSet(MongoModelViewSet):
    queryset = Place.objects.all()
    serializer_class = PlaceSerializer
    permission_classes = [IsAdminUserOrReadOnly,] # allow to managers, not only admins

    def list(self, request):
        serializer = CardSerializer(self.queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def retrieve(self, request, city=None, title=None):
        try:
            cities = City.objects(city=city.capitalize())
            place = self.queryset.get(title=title.capitalize(), address__city__in=cities)
            serializer = self.get_serializer(place)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except mongoengine.DoesNotExist:
            return Response({'message': 'This place does not exist'}, status=status.HTTP_404_NOT_FOUND)

    def create(self, request):
        try:
            place = Place()
            place.title = request.data['title'].capitalize()
            place.phone = request.data['phone']
            review = GeneralReview()
            review.save()
            place.general_review = review
            place.save()
            serializer = self.get_serializer(place)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except mongoengine.errors.NotUniqueError:
            return Response({'message': 'This place already exists'}, status=status.HTTP_400_BAD_REQUEST)
        except mongoengine.errors.ValidationError as e:
            return Response({'error': 'Validation error', 'message': e.errors}, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        try:
            place = self.queryset.get(id=pk)
            serializer = self.get_serializer(place)
            serializer.update(place, request.data)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except mongoengine.DoesNotExist:
            return Response({'message': 'This place does not exist'}, status=status.HTTP_404_NOT_FOUND)
        except mongoengine.errors.NotUniqueError:
            return Response({'message': 'This place already exists'}, status=status.HTTP_400_BAD_REQUEST)
        except mongoengine.errors.ValidationError as e:
            return Response({'error': 'Validation error', 'message': e.errors}, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        try:
            place = self.queryset.get(id=pk)
            place.general_review.delete()
            place.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except mongoengine.DoesNotExist:
            return Response({'message': 'This place does not exist'}, status=status.HTTP_404_NOT_FOUND)


# class FavoriteViewSet(MongoModelViewSet):
#     queryset = Favorite.objects.all()
#     serializer_class = FavoriteSerializer
#     permission_classes = [IsAuthenticated,]

#     def list(self, request):
#         favorites = self.queryset(user_id=request.user.id)
#         serializer = self.get_serializer(favorites, many=True)
#         return Response(serializer.data, status=status.HTTP_200_OK)

#     def handle(self, request, pk=None):
#         try:
#             place = Place.objects.get(id=pk)
#         except mongoengine.DoesNotExist:
#             return Response(status=status.HTTP_404_NOT_FOUND)
        
#         if favorite := self.queryset(user_id=request.user.id, place=place):
#             favorite.delete()
#             return Response(status=status.HTTP_204_NO_CONTENT)
#         else:
#             favorite = Favorite()
#             favorite.user_id = request.user.id
#             favorite.place = place
#             favorite.save()
#             return Response(status=status.HTTP_201_CREATED)


def get_photo(request, pk):
    file_location = f'{settings.MEDIA_ROOT}/{settings.PHOTO_URL}/{pk}'
    with open(file_location, "rb") as f:
        return HttpResponse(f.read(), content_type="image/jpeg")