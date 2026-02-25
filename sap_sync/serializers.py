from rest_framework import serializers
from .models import Products , Party , syncLogs


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Products
        fields = '__all__'
        
class PartySerializer(serializers.ModelSerializer):
    class Meta:
        model = Party
        fields = '__all__'
        
class SyncLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = syncLogs
        fields = '__all__'