from rest_framework import permissions, status, exceptions
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework_simplejwt.tokens import RefreshToken
from django.conf import settings
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.core.mail import send_mail
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.auth.models import User

from .models import *
from .serializers import *


@api_view(['GET'])
@permission_classes([permissions.AllowAny,])
def getPlace(request, id):
    return Response({"response": id}, status=status.HTTP_200_OK)