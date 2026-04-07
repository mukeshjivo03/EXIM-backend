from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from .services import get_exim_rates
from accounts.permissions import HasAppPermission
from rest_framework.permissions import IsAuthenticated


class fetchEximRatesView(APIView):
    def get_permissions(self):
        return [IsAuthenticated(), HasAppPermission('accounts.view_exim_rates')]
    
    def get(self, request):
        date = request.query_params.get('date')
        data = get_exim_rates(date)
        return Response(data)
    
