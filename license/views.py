from django.shortcuts import render
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from .models import AdvanceLicenseHeaders, AdvanceLicenseLines , DFIALicenseHeader , DFIALicenseLines
from .serializers import AdvanceLicenseHeaderSerialzer, AdvanceLicenseLineSerialzer , DFIALicenseheaderCreateSerializer , DFIALicenseLineSerializer ,DFIALicenseListSerializer
from accounts.permissions import IsAdminUser , IsFactoryUser , IsManagerUser
from accounts.permissions import IsAdminUser, IsManagerUser


# Create your views here.
class AdvanceLicenseHeadersListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated, IsAdminUser | IsManagerUser]
    queryset = AdvanceLicenseHeaders.objects.all()
    serializer_class = AdvanceLicenseHeaderSerialzer
    permission_class = [ IsAuthenticated & (IsManagerUser | IsAdminUser)]


class AdvanceLicenseLinesListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated, IsAdminUser | IsManagerUser]
    queryset = AdvanceLicenseLines.objects.all()
    serializer_class = AdvanceLicenseLineSerialzer


 
    
    
class AdvanceLicenseHeaderRetrieveUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated, IsAdminUser | IsManagerUser]
    queryset = AdvanceLicenseHeaders.objects.all()
    serializer_class = AdvanceLicenseHeaderSerialzer
    lookup_field = 'license_no'
    
    
class DFIALicenseHeaderCreateView(generics.CreateAPIView):
    queryset = DFIALicenseHeader.objects.all()
    serializer_class = DFIALicenseheaderCreateSerializer
    permission_class = [ IsAuthenticated & (IsManagerUser | IsAdminUser)]

class DFIALicenseHeaderListView(generics.ListAPIView):
    queryset = DFIALicenseHeader.objects.all()
    serializer_class = DFIALicenseListSerializer
    
class DFIALicenseHeaderRetrieveUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    queryset = DFIALicenseHeader.objects.all()
    serializer_class = DFIALicenseListSerializer
    lookup_field = 'file_no'
    
    
    
    
    

class DFIALicenseLinesListCreateView(generics.ListCreateAPIView):
    queryset = DFIALicenseLines.objects.all()
    serialzer_class= DFIALicenseLineSerializer
    permission_class = [ IsAuthenticated & (IsManagerUser | IsAdminUser)]
    

    
    


    