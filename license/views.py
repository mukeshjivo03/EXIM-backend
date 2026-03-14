from django.shortcuts import render
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from .models import AdvanceLicenseHeaders, AdvanceLicenseLines , DFIALicenseHeader , DFIALicenseLines
from .serializers import AdvanceLicenseHeaderSerialzer, AdvanceLicenseLineSerialzer, AdvanceLicenseHeaderCreateSerialzer, DFIALicenseheaderCreateSerializer , DFIALicenseLineSerializer ,DFIALicenseListSerializer
from accounts.permissions import IsAdminUser , IsFactoryUser , IsManagerUser
from accounts.permissions import IsAdminUser, IsManagerUser


class AdvanceLicenseHeadersListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated, IsAdminUser | IsManagerUser]
    queryset = AdvanceLicenseHeaders.objects.all()
    serializer_class = AdvanceLicenseHeaderCreateSerialzer
    permission_class = [ IsAuthenticated & (IsManagerUser | IsAdminUser)]


class AdvanceLicenseHeaderRetrieveUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated, IsAdminUser | IsManagerUser]
    queryset = AdvanceLicenseHeaders.objects.all()
    serializer_class = AdvanceLicenseHeaderCreateSerialzer
    lookup_field = 'license_no'
        
    
class AdvanceLicenseLinesListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated, IsAdminUser | IsManagerUser]
    queryset = AdvanceLicenseLines.objects.all()
    serializer_class = AdvanceLicenseLineSerialzer
    
class AdvanceLicenseLinesRetrieveUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated, IsAdminUser | IsManagerUser]
    queryset = AdvanceLicenseLines.objects.all()
    serializer_class = AdvanceLicenseLineSerialzer
    lookup_field = 'id'
    
        
    
    
    

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
    

    
    
    

class DFIALicenseLinesCreateView(generics.CreateAPIView):
    queryset = DFIALicenseLines.objects.all()
    serializer_class = DFIALicenseLineSerializer  # ← fixed
    permission_classes = [IsAuthenticated & (IsManagerUser | IsAdminUser)]  # ← also 'classes' not 'class'

class DFIALicenseLinesListView(generics.ListAPIView):
    queryset = DFIALicenseLines.objects.all()
    serializer_class = DFIALicenseLineSerializer  # ← fixed
    permission_classes = [IsAuthenticated & (IsManagerUser | IsAdminUser)]  # ← also 'classes' not 'class'

class DFIALicenseLinesRetrieveUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    queryset = DFIALicenseLines.objects.all()
    serializer_class = DFIALicenseLineSerializer
    lookup_field = 'id'
    
    
    

    
    


    