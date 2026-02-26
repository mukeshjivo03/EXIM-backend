from rest_framework import serializers
from .models import RMProducts ,FGProducts , Party , syncLogs


class RMProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = RMProducts
        fields = '__all__'
        
class FGProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = FGProducts
        fields = '__all__'
        
class PartySerializer(serializers.ModelSerializer):
    class Meta:
        model = Party
        fields = '__all__'
        
class SyncLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = syncLogs
        fields = '__all__'