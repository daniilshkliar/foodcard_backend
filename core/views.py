import json
import mongoengine
import base64
import os
from PIL import Image as PILImage
from io import BytesIO
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

            if main_photo := request.data.pop('main_photo'):
                try:
                    photo = Image.objects.get(id=main_photo)
                    if photo in place.photos:
                        place.main_photo = photo
                        place.save()
                except mongoengine.DoesNotExist:
                    return Response({'message': 'This main photo does not exist'}, status=status.HTTP_404_NOT_FOUND)

            serializer = self.get_serializer(place, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
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


class ImageViewSet(MongoModelViewSet):
    queryset = Image.objects.all()
    serializer_class = ImageSerializer
    permission_classes = (IsAdminUserOrReadOnly|IsManagerOrReadOnly,)
    
    def retrieve(self, request, file_name=None):
        file_location = os.path.join(settings.MEDIA_ROOT, 'images', file_name)
        with open(file_location, "rb") as f:
            return HttpResponse(f.read(), content_type="image/jpeg")

    def create(self, request, pk=None):
        try:
            place = Place.objects.get(id=pk)

            if photos := request.data.get('photos'):
                size = (300, 200)
                new_images = []
                for photo in photos:
                    name = str(uuid.uuid4())
                    image_name = f'{name}.jpg'
                    thumbnail_name = f'{name}.thumbnail'
                    image_uri = os.path.join(settings.URI_ROOT, 'core/image/get/', image_name)
                    thumbnail_uri = os.path.join(settings.URI_ROOT, 'core/image/get/', thumbnail_name)
                    image_location = os.path.join(settings.MEDIA_ROOT, 'images', image_name)
                    thumbnail_location = os.path.join(settings.MEDIA_ROOT, 'images', thumbnail_name)

                    try:
                        with PILImage.open(BytesIO(base64.b64decode(photo))) as img:
                            img.save(image_location, 'JPEG')
                            img.thumbnail(size)
                            img.save(thumbnail_location, 'JPEG')
                    except:
                        Response({'message': 'OSError'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                    
                    new_image = Image(
                        image_name=image_name,
                        thumbnail_name=thumbnail_name,
                        image_uri=image_uri,
                        thumbnail_uri=thumbnail_uri
                    ).save()

                    new_images.append(new_image)

                place.photos.extend(new_images)
                place.save()
            else:
                return Response({'message': 'You must provide any photos'}, status=status.HTTP_400_BAD_REQUEST)

            serializer = PlaceSerializer(place)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except mongoengine.DoesNotExist:
            return Response({'message': 'This place does not exist'}, status=status.HTTP_404_NOT_FOUND)

    def destroy(self, request, pk=None):
        try:
            place = Place.objects.get(id=pk)
            if photos := request.data.get('photos'):
                for photo_id in photos:
                    photo = self.queryset.get(id=photo_id)
                    if photo in place.photos:
                        try:
                            os.remove(os.path.join(settings.MEDIA_ROOT, 'images', photo.image_name))
                            os.remove(os.path.join(settings.MEDIA_ROOT, 'images', photo.thumbnail_name))
                            place.photos.remove(photo)
                        except:
                            print("File does not exist")
            else:
                return Response({'message': 'You must provide any photos'}, status=status.HTTP_400_BAD_REQUEST)

            place.save()
            serializer = PlaceSerializer(place)
            return Response(serializer.data, status=status.HTTP_200_OK)
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