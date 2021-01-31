import mongoengine
import os
import json
from django.conf import settings
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework_mongoengine.viewsets import ModelViewSet as MongoModelViewSet

from .models import *
from .serializers import *
from backend.permissions import *
from authentication.models import *
from core.models import Place


class ReservationViewSet(MongoModelViewSet):
    queryset = Reservation.objects.all()
    serializer_class = ReservationSerializer
    permission_classes = (AllowAny,)

    def list(self, request, pk=None):
        data = json.loads(self.queryset(place=pk).to_json())
        return Response(data, status=status.HTTP_200_OK)

    # def retrieve(self, request, city=None, title=None):
    #     try:
    #         place = self.queryset.get(title=title.capitalize(), address__city=city.capitalize(), is_active=True)
    #         serializer = self.get_serializer(place)
    #         return Response(serializer.data, status=status.HTTP_200_OK)
    #     except mongoengine.DoesNotExist:
    #         return Response({'message': 'This place does not exist'}, status=status.HTTP_404_NOT_FOUND)

    def create(self, request, pk=None):
        try:
            place = Place.objects.get(id=pk)
            request.data['place'] = place.id
            if request.user.id:
                request.data['user'] = request.user.id
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except mongoengine.DoesNotExist:
            return Response({'message': 'This place does not exist'}, status=status.HTTP_404_NOT_FOUND)

    # def update(self, request, pk=None):
    #     try:
    #         place = self.queryset.get(id=pk)

    #         if main_photo := request.data.pop('main_photo', None):
    #             try:
    #                 photo = Image.objects.get(id=main_photo)
    #                 if photo in place.photos:
    #                     place.main_photo = photo
    #                     place.save()
    #             except mongoengine.DoesNotExist:
    #                 return Response({'message': 'This main photo does not exist'}, status=status.HTTP_404_NOT_FOUND)

    #         serializer = self.get_serializer(place, data=request.data, partial=True)
    #         serializer.is_valid(raise_exception=True)
    #         serializer.save()
    #         return Response(serializer.data, status=status.HTTP_200_OK)
    #     except mongoengine.DoesNotExist:
    #         return Response({'message': 'This place does not exist'}, status=status.HTTP_404_NOT_FOUND)

    # def destroy(self, request, pk=None):
    #     try:
    #         place = self.queryset.get(id=pk)
    #         place.is_active = False
    #         place.save()
    #         # place.general_review.delete()
    #         # # delete all photos
    #         # place.delete()
    #         return Response(status=status.HTTP_204_NO_CONTENT)
    #     except mongoengine.DoesNotExist:
    #         return Response({'message': 'This place does not exist'}, status=status.HTTP_404_NOT_FOUND)
