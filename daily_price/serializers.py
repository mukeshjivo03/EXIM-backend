from rest_framework import serializers
from .models import DailyPrice , JivoRates


class DailyPriceSerializer(serializers.ModelSerializer):
    class Meta:
        model = DailyPrice
        fields = '__all__'

class JivoRatesSerializer(serializers.ModelSerializer):
    class Meta:
        model = JivoRates
        fields = '__all__'
