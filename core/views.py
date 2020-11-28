# from django.contrib.auth import get_user_model
# from django.core import serializers as sr
# from rest_framework.views import APIView
# from rest_framework import viewsets
# from rest_framework.decorators import api_view, permission_classes
# from rest_framework_simplejwt.views import TokenObtainPairView
# from rest_framework_simplejwt.tokens import RefreshToken
# from django.http import HttpResponseRedirect, HttpResponse
# from rest_framework.parsers import MultiPartParser, FormParser
# import base64
# from django.db.models import Q
# from django.db import connection
# from django.http import JsonResponse
# import datetime
# from io import BytesIO
# from reportlab.pdfgen import canvas
# import json
# from mongoengine import Document
import json
import mongoengine
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

    def retrieve(self, request, city=None, title=None):
        try:
            place = self.queryset.get(title=title.capitalize(), address__city=city.capitalize())
            data = json.loads(place.to_json())
            data['categories'] = [category.title for category in place.categories]
            return Response(data, status=status.HTTP_200_OK)
        except mongoengine.DoesNotExist:
            return Response({"response": "error", "message" : "Not found"}, status=status.HTTP_404_NOT_FOUND)


class CategoryViewSet(MongoModelViewSet):

    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [AllowAny,]