import json
from rest_framework import permissions, status, exceptions
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from rest_framework_simplejwt.tokens import RefreshToken
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.core.mail import send_mail
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.auth.models import User
from rest_framework_mongoengine.viewsets import ModelViewSet as MongoModelViewSet

from .models import *   
from .serializers import *


class UserViewSet(MongoModelViewSet):
    
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated,]

    def retrieve(self, request):
        try:
            uid = json.loads(urlsafe_base64_decode(request.META['HTTP_AUTHORIZATION'].split('.')[1]).decode())['user_id']
            user = get_object_or_404(self.queryset, pk=uid)
        except(TypeError, ValueError):
            user = None
            
        if user:
            serializer = self.get_serializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({"response": "error", "message" : "Bad request"}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([permissions.AllowAny,])
def signup(request):
    serializer = SignupSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save(is_active=False)
        if user:
            activationToken = PasswordResetTokenGenerator()
            plain_message = f"""
                Hi {user.first_name}.
                Please click on the link below to confirm your registration:
                {settings.CORS_ORIGIN_WHITELIST[0]}/activate/{urlsafe_base64_encode(force_bytes(user.pk)).decode()}/{activationToken.make_token(user)}/
                """
            subject = 'Activate your FOODCARD account'
            from_email = settings.EMAIL_HOST_USER
            to = user.email
            send_mail(subject, plain_message, from_email, [to])
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response({"response": "error", "message": "Internal server error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        return Response({"response": "error", "message" : serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([permissions.AllowAny,])
def activateAccount(request, uidb64, utoken):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = get_object_or_404(User, pk=uid)
    except(TypeError, ValueError):
        user = None
        
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
        return Response({"response": "error", "message" : "Bad request"}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([permissions.AllowAny,])
def login(request):
    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid():
        max_age = settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME'].total_seconds()
        response = Response()
        response.set_cookie(key='refresh', value=serializer.data['tokens'], httponly=True, max_age=max_age)
        response.data = {'access': str(serializer.data['tokens'].access_token)}
        return response
    else:
        return Response({"response": "error", "message" : serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([permissions.AllowAny,])
def token_refresh(request):
    tokens = RefreshToken(request.COOKIES.get('refresh'))
    if tokens:
        tokens.set_jti()
        tokens.set_exp()
        max_age = settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME'].total_seconds()
        response = Response()
        response.set_cookie(key='refresh', value=str(tokens), httponly=True, max_age=max_age)
        response.data = {'access': str(tokens.access_token)}
        return response
    else:
        return Response({"response": "error", "message" : "Bad request"}, status=status.HTTP_400_BAD_REQUEST)