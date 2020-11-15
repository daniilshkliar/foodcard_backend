from rest_framework.decorators import api_view, permission_classes
from rest_framework import permissions, status
from rest_framework.response import Response
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core.mail import send_mail
from django.conf import settings
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User
from rest_framework import exceptions

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
        tokens = RefreshToken.for_user(user)
        max_age = settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME'].total_seconds()
        response = Response()
        response.set_cookie(key='refresh', value=tokens, httponly=True, max_age=max_age)
        response.data = {'access': str(tokens.access_token)}
        return response
    else:
        return Response({"response" : "error"}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([permissions.AllowAny,])
def login(request):
    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid():
        user = User.objects.filter(email=request.data.get('email')).first()
        if user and user.check_password(request.data.get('password')):
            tokens = RefreshToken.for_user(user)
            max_age = settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME'].total_seconds()
            response = Response()
            response.set_cookie(key='refresh', value=tokens, httponly=True, max_age=max_age)
            response.data = {'access': str(tokens.access_token)}
            return response
        else:
            raise exceptions.AuthenticationFailed('No active account found with the given credentials')
    else:
        return Response({"response" : "error", "message" : serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([permissions.AllowAny,])
def token_refresh(request):
    tokens = RefreshToken(request.COOKIES.get('refresh'))
    tokens.set_jti()
    tokens.set_exp()
    max_age = settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME'].total_seconds()
    response = Response()
    response.set_cookie(key='refresh', value=str(tokens), httponly=True, max_age=max_age)
    response.data = {'access': str(tokens.access_token)}
    return response


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated,])
def isit(request):
    return Response({"response": "yes"}, status=status.HTTP_200_OK)