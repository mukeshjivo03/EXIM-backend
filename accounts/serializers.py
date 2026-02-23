from rest_framework import serializers
from .models import User
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id'  , 'name' , 'email' , 'role']

    def update(self, instance, validated_data):
            password = validated_data.pop('password', None)
            if password:
                instance.set_password(password)

            return super().update(instance, validated_data)        
        
  
class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})
    
    class Meta:
        model = User
        fields = ['name' , 'email' , 'password' , 'role']
        
        
    def create(self, validated_data):
        return User.objects.create_user(
            email=validated_data['email'],
            name=validated_data['name'],
            role=validated_data.get('role', 'FTR'),
            password=validated_data['password']
        )
     

class MyTokenObtainSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user) 
        
        token['role'] = user.role
        token['name'] = user.name
        return token
    
    def validate(self, attrs):
        data = super().validate(attrs)
        data['name'] = self.user.name
        data['email'] = self.user.email
        data['role'] = self.user.role
        data['id'] = self.user.id

        return data