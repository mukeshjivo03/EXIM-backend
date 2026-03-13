from django.shortcuts import render
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from .models import AdvanceLicenseHeaders, AdvanceLicenseLines , DFIALicenseHeader , DFIALicenseLines
from .serializers import AdvanceLicenseHeaderSerialzer, AdvanceLicenseLineSerialzer , DFIALicenseheaderSerializer , DFIALicenseLineSerializer
from accounts.permissions import IsAdminUser , IsFactoryUser , IsManagerUser


# Create your views here.
class AdvanceLicenseHeadersListCreateView(generics.ListCreateAPIView):
    queryset = AdvanceLicenseHeaders.objects.all()
    serializer_class = AdvanceLicenseHeaderSerialzer
    permission_class = [ IsAuthenticated & (IsManagerUser | IsAdminUser)]


class AdvanceLicenseLinesListCreateView(generics.ListCreateAPIView):
    queryset = AdvanceLicenseLines.objects.all()
    serializer_class = AdvanceLicenseLineSerialzer
    permission_class = [ IsAuthenticated & (IsManagerUser | IsAdminUser)]
    
    
    
class AdvanceLicenseRetrieveDeleteView(generics.RetrieveDestroyAPIView):
    queryset = AdvanceLicenseHeaders.objects.all()
    serializer_class = AdvanceLicenseHeaderSerialzer
    lookup_field = 'license_no'
    permission_class = [ IsAuthenticated & (IsManagerUser | IsAdminUser)]
    
    
class DFIALicenseHeaderListCreateView(generics.ListCreateAPIView):
    queryset = DFIALicenseHeader.objects.all()
    serializer_class = DFIALicenseheaderSerializer
    permission_class = [ IsAuthenticated & (IsManagerUser | IsAdminUser)]

class DFIALicenseLinesListCreateView(generics.ListCreateAPIView):
    queryset = DFIALicenseLines.objects.all()
    serialzer_class= DFIALicenseLineSerializer
    permission_class = [ IsAuthenticated & (IsManagerUser | IsAdminUser)]
    
class DFIALicenseHeaderRetrieveUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    queryset = DFIALicenseHeader.objects.all()
    serializer_class = DFIALicenseheaderSerializer
    lookup_field = 'file_no'
    permission_class = [ IsAuthenticated & (IsManagerUser | IsAdminUser)]
    
    
    


    