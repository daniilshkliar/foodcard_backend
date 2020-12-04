import json
import mongoengine
from django.shortcuts import get_object_or_404
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from rest_framework_mongoengine.viewsets import ModelViewSet as MongoModelViewSet

from .models import *   
from .serializers import *


class PlaceViewSet(MongoModelViewSet):
    queryset = Place.objects.all()
    serializer_class = PlaceSerializer
    permission_classes = [AllowAny,]

    def list(self, request):
        serializer = self.get_serializer(self.queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def retrieve(self, request, city=None, title=None):
        try:
            place = self.queryset.get(title=title.capitalize(), address__city=city.capitalize())
            serializer = self.get_serializer(place)
            return Response(serializer.data, status=status.HTTP_200_OK)
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

    def handle(self, request, place_id=None):
        try:
            place = Place.objects.get(id=place_id)
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
