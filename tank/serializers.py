from rest_framework import serializers
from .models import TankItem, TankData

class TankItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = TankItem
        fields = '__all__'

class TankDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = TankData
        fields = '__all__'

        