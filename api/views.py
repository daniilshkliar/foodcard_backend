from rest_framework.decorators import api_view, permission_classes
from rest_framework import permissions, status
from rest_framework.response import Response

from .models import *
from .serializers import *


@api_view(['POST'])
@permission_classes([permissions.AllowAny,])
def signup(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        if user:
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response({"response" : "error", "message" : {"HTTP_500" : "Internal server error"}}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        return Response({"response" : "error", "message" : serializer.errors}, status=status.HTTP_400_BAD_REQUEST)