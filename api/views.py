from rest_framework.decorators import api_view, permission_classes
from rest_framework import permissions, status
from rest_framework.response import Response

from .models import *
from .serializers import *


@api_view(['GET'])
@permission_classes([permissions.AllowAny,])
def get_user(request):    
    serializer = CurrentUser(request.user)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([permissions.AllowAny,])
def signup(request):
    serializer = Signup(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
    if user:
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    else:
        return Response({"response" : "error", "message" : serializer.errors}, status=status.HTTP_400_BAD_REQUEST)