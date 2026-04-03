from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from .services import get_exim_rates
import requests


class fetchEximRatesView(APIView):
    def get(self, request):
        date = request.query_params.get('date')
        data = get_exim_rates(date)
        return Response(data)
    
