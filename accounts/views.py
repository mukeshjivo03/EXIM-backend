from django.shortcuts import render
from rest_framework import generics
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import IsAuthenticated , AllowAny

from .models import User
from .serializers import UserSerializer , UserRegistrationSerializer , MyTokenObtainSerializer
 
# User Management 
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer

class ListUservView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    
    
class GetDeleteUpdate(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_field = 'id'
   
# LOGIN
class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainSerializer
    
# LOGOUT 
class Logout(APIView):
    def post(self, request):
        try :
            refresh_token = request.data["refresh_token"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)