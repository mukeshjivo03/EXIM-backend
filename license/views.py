from django.shortcuts import render
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .models import AdvanceLicenseHeaders, AdvanceLicenseLines
from .serializers import AdvanceLicenseHeaderSerialzer, AdvanceLicenseLineSerialzer


# Create your views here.
class AdvanceLicenseHeadersListCreateView(generics.ListCreateAPIView):
    queryset = AdvanceLicenseHeaders.objects.all()
    serializer_class = AdvanceLicenseHeaderSerialzer


class AdvanceLicenseLinesListCreateView(generics.ListCreateAPIView):
    queryset = AdvanceLicenseLines.objects.all()
    serializer_class = AdvanceLicenseLineSerialzer
    
    
class AdvanceLicenseRetrieveDeleteView(generics.RetrieveDestroyAPIView):
    queryset = AdvanceLicenseHeaders.objects.all()
    serializer_class = AdvanceLicenseHeaderSerialzer
    lookup_field = 'license_no'
    


    