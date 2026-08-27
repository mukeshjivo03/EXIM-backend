from django.shortcuts import render
from rest_framework import generics
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import IsAuthenticated , AllowAny

from .models import User
from .permissions import HasAppPermission
from .serializers import UserSerializer , UserRegistrationSerializer , MyTokenObtainSerializer
 
# User Management 
class RegisterView(generics.CreateAPIView):
    def get_permissions(self):
        return [IsAuthenticated() , HasAppPermission('accounts.add_user')]

    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer

class ListUservView(generics.ListAPIView):
    def get_permissions(self):
        return [IsAuthenticated() , HasAppPermission('accounts.view_user')]

    queryset = User.objects.all()
    serializer_class = UserSerializer


class GetDeleteUpdate(generics.RetrieveUpdateDestroyAPIView):
    # One endpoint, three levels of access: reading a user is not the same
    # right as editing one, and neither implies being able to delete one.
    METHOD_PERMISSIONS = {
        'GET': 'accounts.view_user',
        'PUT': 'accounts.change_user',
        'PATCH': 'accounts.change_user',
        'DELETE': 'accounts.delete_user',
    }

    def get_permissions(self):
        perm = self.METHOD_PERMISSIONS.get(self.request.method, 'accounts.view_user')
        return [IsAuthenticated() , HasAppPermission(perm)]

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