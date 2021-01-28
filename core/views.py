import mongoengine
import base64
import os
from PIL import Image as PILImage
from io import BytesIO
from django.conf import settings
from django.http import HttpResponse
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
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

            if main_photo := request.data.pop('main_photo', None):
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
            place.is_active = False
            place.save()
            # place.general_review.delete()
            # # delete all photos
            # place.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except mongoengine.DoesNotExist:
            return Response({'message': 'This place does not exist'}, status=status.HTTP_404_NOT_FOUND)


class BaseImageViewSet():    
    def get_image(self, file_name):
        try:
            file_path = os.path.join(settings.MEDIA_ROOT, 'images', file_name)
            with open(file_path, 'rb') as f:
                return f.read()
        except FileNotFoundError:
            print(f'File {file_name} not found')
            return None

    def save_images(self, images, thumbnail=True):
        thumbnail_size = (300, 200)
        saved_images = []

        for image in images:
            image_id = str(uuid.uuid4())
            image_name = f'{image_id}.jpeg'
            image_uri = os.path.join(settings.URI_ROOT, 'core/image/get/', image_name)
            image_path = os.path.join(settings.MEDIA_ROOT, 'images', image_name)

            if thumbnail:
                thumbnail_name = f'{image_id}.thumbnail'
                thumbnail_uri = os.path.join(settings.URI_ROOT, 'core/image/get/', thumbnail_name)
                thumbnail_path = os.path.join(settings.MEDIA_ROOT, 'images', thumbnail_name)
            else:
                thumbnail_name = None
                thumbnail_uri = None

            try:
                with PILImage.open(BytesIO(base64.b64decode(image))) as img:
                    img.save(image_path, 'JPEG')
                    if thumbnail:
                        img.thumbnail(thumbnail_size)
                        img.save(thumbnail_path, 'JPEG')
            except OSError:
                print('OSError')
                continue
            
            saved_image = Image(
                image_name=image_name,
                thumbnail_name=thumbnail_name,
                image_uri=image_uri,
                thumbnail_uri=thumbnail_uri
            ).save()

            saved_images.append(saved_image)
            
        return saved_images

    def delete_image(self, image):
        try:
            os.remove(os.path.join(settings.MEDIA_ROOT, 'images', image.image_name))
            if image.thumbnail_name:
                os.remove(os.path.join(settings.MEDIA_ROOT, 'images', image.thumbnail_name))
        except FileNotFoundError:
            return False
        
        return True


class PlaceImageViewSet(BaseImageViewSet, MongoModelViewSet):
    queryset = Image.objects.all()
    serializer_class = ImageSerializer
    permission_classes = (IsAdminUserOrReadOnly|IsManagerOrReadOnly,)
    
    def retrieve(self, request, file_name=None):
        return HttpResponse(self.get_image(file_name), content_type="image/jpeg")

    def create(self, request, pk=None):
        try:
            place = Place.objects.get(id=pk)

            if photos := request.data.get('photos'):
                images = self.save_images(photos)
                place.photos.extend(images)
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
                    if photo in place.photos and self.delete_image(photo):
                        place.photos.remove(photo)
                        photo.delete()
                if place.main_photo in photos:
                    place.main_photo.delete()
                place.save()
            else:
                return Response({'message': 'You must provide any photos'}, status=status.HTTP_400_BAD_REQUEST)

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