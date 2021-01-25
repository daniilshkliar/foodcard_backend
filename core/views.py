import json
import mongoengine
import base64
import os
from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from rest_framework_mongoengine.viewsets import ModelViewSet as MongoModelViewSet

from backend.permissions import *
from .models import *   
from authentication.models import *
from .serializers import *


class PlaceViewSet(MongoModelViewSet):
    queryset = Place.objects.all()
    serializer_class = PlaceSerializer
    permission_classes = (IsAdminUserOrReadOnly|ManagerUpdateOnly,)

    def list(self, request):
        serializer = CardSerializer(self.queryset(is_active=True), many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def retrieve(self, request, city=None, title=None):
        try:
            place = self.queryset.get(title=title.capitalize(), address__city=city.capitalize(), is_active=True)
            serializer = self.get_serializer(place)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except mongoengine.DoesNotExist:
            return Response({'message': 'This place does not exist'}, status=status.HTTP_404_NOT_FOUND)

    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, pk=None):
        try:
            place = self.queryset.get(id=pk)
            serializer = self.get_serializer(place, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        except mongoengine.DoesNotExist:
            return Response({'message': 'This place does not exist'}, status=status.HTTP_404_NOT_FOUND)

    def upload_image(self, request, pk=None):
        try:
            place = self.queryset.get(id=pk)

            if photos := request.data.get('photos'):
                photo_urls = []
                for photo in photos:
                    file_name = f'{str(uuid.uuid4())}.jpg'
                    file_location = f'{settings.MEDIA_ROOT}/{settings.PHOTO_URL}/{file_name}'
                    uri = f'{settings.URI_ROOT}core/photo/get/{file_name}'
                    with open(file_location, 'wb') as f:
                        f.write(base64.b64decode(photo))
                        photo_urls.append(uri)
                place.photos.extend(photo_urls)
                place.save()
            else:
                return Response({'message': 'You must provide any photos'}, status=status.HTTP_400_BAD_REQUEST)

            serializer = self.get_serializer(place)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except mongoengine.DoesNotExist:
            return Response({'message': 'This place does not exist'}, status=status.HTTP_404_NOT_FOUND)

    def delete_image(self, request, pk=None):
        try:
            place = self.queryset.get(id=pk)

            if photos := request.data.get('photos'):
                for photo in photos:
                    if photo in place.photos:
                        try:
                            os.remove(f'{settings.MEDIA_ROOT}/{settings.PHOTO_URL}/{photo.split("/")[-1]}')
                            place.photos.remove(photo)
                        except:
                            print("File does not exist")
            else:
                return Response({'message': 'You must provide any photos'}, status=status.HTTP_400_BAD_REQUEST)

            place.save()
            serializer = self.get_serializer(place)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except mongoengine.DoesNotExist:
            return Response({'message': 'This place does not exist'}, status=status.HTTP_404_NOT_FOUND)

    def destroy(self, request, pk=None):
        try:
            place = self.queryset.get(id=pk)
            place.general_review.delete()
            place.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except mongoengine.DoesNotExist:
            return Response({'message': 'This place does not exist'}, status=status.HTTP_404_NOT_FOUND)


class FavoriteViewSet(MongoModelViewSet):
    queryset = Favorite.objects.all()
    serializer_class = FavoriteSerializer
    permission_classes = (IsAuthenticated,)

    def list(self, request):
        serializer = self.get_serializer(self.queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def retrieve(self, request):
        try:
            favorite = self.queryset.get(user=request.user.id)
            serializer = self.get_serializer(favorite)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except mongoengine.DoesNotExist:
            return Response({'message': 'User has no favorite places'}, status=status.HTTP_404_NOT_FOUND)

    def handle(self, request, pk=None):
        try:
            place = Place.objects.get(id=pk)
        except mongoengine.DoesNotExist:
            return Response({'message': 'This place does not exist'}, status=status.HTTP_404_NOT_FOUND)
        
        try:
            favorite = Favorite.objects.get(user=request.user.id)
        except mongoengine.DoesNotExist:
            favorite = Favorite(user=request.user.id).save()
        
        if place in favorite.places:
            favorite.places.remove(place)
            favorite.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            favorite.places.append(place)
            favorite.save()
            return Response(status=status.HTTP_201_CREATED)


class ControlPanelViewSet(MongoModelViewSet):
    queryset = Place.objects.all()
    serializer_class = PlacesForControlPanelSerializer
    permission_classes = (IsAdminUserOrManager,)

    def list(self, request):
        if request.user.is_staff:
            serializer = self.get_serializer(self.queryset, many=True)
        else:
            manager = Manager.objects.get(user=request.user.id)
            serializer = self.get_serializer(manager.places, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def retrieve(self, request, pk=None):
        try:
            place = self.queryset.get(id=pk)
            serializer = PlaceSerializer(place)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except mongoengine.DoesNotExist:
            return Response({'message': 'This place does not exist'}, status=status.HTTP_404_NOT_FOUND)


def get_photo(request, pk):
    file_location = f'{settings.MEDIA_ROOT}/{settings.PHOTO_URL}/{pk}'
    with open(file_location, "rb") as f:
        return HttpResponse(f.read(), content_type="image/jpeg")