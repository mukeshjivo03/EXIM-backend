from rest_framework import serializers
from .models import User
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'name', 'email']  # removed role

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        if password:
            instance.set_password(password)
        return super().update(instance, validated_data)


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})

    class Meta:
        model = User
        fields = ['name', 'email', 'password']  # removed role

    def create(self, validated_data):
        return User.objects.create_user(
            email=validated_data['email'],
            name=validated_data['name'],
            password=validated_data['password']
        )

class MyTokenObtainSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['name'] = user.name  
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        
        # Standard user data
        data['name'] = self.user.name
        data['email'] = self.user.email
        data['id'] = self.user.id
        
        # Fetch raw permissions (e.g., {'tank.delete_tankdata', 'tank.view_tanklog'})
        raw_permissions = self.user.get_all_permissions()
        
        structured_perms = {}
        
        for perm in raw_permissions:
            try:
                # 1. Split app and action+model (e.g., "tank", "delete_tankdata")
                app, action_model = perm.split('.')
                
                # 2. Split action and model (e.g., "delete", "tankdata")
                # Using maxsplit=1 ensures models with underscores (like 'tank_log') don't break the split
                action, model_name = action_model.split('_', 1)
                
                # 3. Append to the dictionary
                if model_name not in structured_perms:
                    structured_perms[model_name] = []
                    
                structured_perms[model_name].append(action)
                
            except ValueError:
                # If a custom permission doesn't follow the "app.action_model" standard, skip it
                continue
                
        # Assign the structured dictionary instead of the flat list
        data['permissions'] = structured_perms  
        
        return data