from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.core import serializers as sr
from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from django.http import HttpResponseRedirect, HttpResponse
from rest_framework.parsers import MultiPartParser, FormParser
import base64
from django.db.models import Q
from django.db import connection
from django.http import JsonResponse
import datetime
from io import BytesIO
from reportlab.pdfgen import canvas
import json
from mongoengine import Document

from .models import *
from .serializers import *


class PlaceSetter(APIView):
    permission_classes = [permissions.AllowAny,]
    
    def get(self, request, *args, **kwargs):
        # cat1 = Category(title='qwer').save()
        # cat2 = Category(title='asdf').save()
        # place = Place(title='zcxv', phone="adsffdsadf", description="adsffdasfdsfd")
        # place.categories.extend([cat1, cat2])
        # place.save()
        # delete(Category.objects.get(title='asdf'))
        return Response({"serializer.data": "dasf"}, status=status.HTTP_200_OK)