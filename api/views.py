from rest_framework.decorators import api_view, permission_classes
from rest_framework import permissions, status
from rest_framework.response import Response
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.conf import settings
from django.utils.html import strip_tags
from rest_framework_simplejwt.tokens import RefreshToken

from django.contrib.auth.models import User

from .models import *
from .serializers import *


@api_view(['POST'])
@permission_classes([permissions.AllowAny,])
def signup(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save(is_active=False)
        if user:
            activationToken = PasswordResetTokenGenerator()

            subject = 'Activate your FOODCARD account'
            plain_message = f"""
                Hi {user.first_name}.
                Please click on the link below to confirm your registration:
                {settings.CORS_ORIGIN_WHITELIST[0]}/activate/{urlsafe_base64_encode(force_bytes(user.pk))}/{activationToken.make_token(user)}/
                """
            from_email = settings.EMAIL_HOST_USER
            to = user.email

            send_mail(subject, plain_message, from_email, [to])
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response({"response" : "error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        return Response({"response" : "error", "message" : serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([permissions.AllowAny,])
def activateAccount(request, uidb64, utoken):
    uid = urlsafe_base64_decode(uidb64)
    user = User.objects.get(pk=uid)
    activationToken = PasswordResetTokenGenerator()

    if user and activationToken.check_token(user, utoken):
        user.is_active = True
        user.save()
        refreshedToken = RefreshToken.for_user(user)
        if refreshedToken:
            return Response({
                'refresh': str(refreshedToken),
                'access': str(refreshedToken.access_token),
            }, status=status.HTTP_200_OK)
        else:
            return Response({"response" : "error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        return Response({"response" : "error"}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated,])
def isit(request):
    return Response({"response": "yes"}, status=status.HTTP_200_OK)