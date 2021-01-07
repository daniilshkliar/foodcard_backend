import json
import mongoengine
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
            return Response({'message': 'This ' + self.desciption + ' already exists'}, status=status.HTTP_400_BAD_REQUEST)
        except mongoengine.errors.ValidationError:
            return Response({'message': 'Validation error'}, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        pass

    def destroy(self, request, pk=None):
        try:
            obj = self.queryset.get(id=pk)
            obj.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except mongoengine.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)


class CategoryViewSet(DocumentListViewSet):
    model = Category
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    desciption = 'category'


class CuisineViewSet(DocumentListViewSet):
    model = Cuisine
    queryset = Cuisine.objects.all()
    serializer_class = CuisineSerializer
    desciption = 'cuisine'


class AdditionalServiceViewSet(DocumentListViewSet):
    model = AdditionalService
    queryset = AdditionalService.objects.all()
    serializer_class = AdditionalServiceSerializer
    desciption = 'additional service'


class PlaceViewSet(MongoModelViewSet):
    queryset = Place.objects.all()
    serializer_class = PlaceSerializer
    permission_classes = [IsAdminUserOrReadOnly,]

    def list(self, request):#cards
        serializer = self.get_serializer(self.queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def retrieve(self, request, city=None, title=None):
        try:
            place = self.queryset.get(title=title.capitalize(), address__city=city.capitalize())
            serializer = self.get_serializer(place)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except mongoengine.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def create(self, request):
        try:
            # through serializer validation
            place = Place()
            place.title = request.data['title'].capitalize()
            place.phone = request.data['phone']
            place.save()
            serializer = self.get_serializer(place)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except mongoengine.errors.NotUniqueError:
            return Response({'message': 'This place already exists'}, status=status.HTTP_400_BAD_REQUEST)
        except mongoengine.errors.ValidationError:
            return Response({'message': 'Validation error'}, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        pass

    def destroy(self, request, pk=None):
        try:
            place = self.queryset.get(id=pk)
            place.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except mongoengine.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)


class FavoriteViewSet(MongoModelViewSet):
    queryset = Favorite.objects.all()
    serializer_class = FavoriteSerializer
    permission_classes = [IsAuthenticated,]

    def list(self, request):
        favorites = self.queryset(user_id=request.user.id)
        serializer = self.get_serializer(favorites, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def handle(self, request, pk=None):
        try:
            place = Place.objects.get(id=pk)
        except mongoengine.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
        if favorite := self.queryset(user_id=request.user.id, place=place):
            favorite.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            favorite = Favorite()
            favorite.user_id = request.user.id
            favorite.place = place
            favorite.save()
            return Response(status=status.HTTP_201_CREATED)
