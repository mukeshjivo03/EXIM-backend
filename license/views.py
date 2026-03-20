from django.shortcuts import render
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Sum

from .models import AdvanceLicenseHeaders, AdvanceLicenseLines , DFIALicenseHeader , DFIALicenseLines
from .serializers import AdvanceLicenseHeaderSerialzer, AdvanceLicenseLineSerialzer, AdvanceLicenseHeaderCreateSerialzer, DFIALicenseheaderCreateSerializer , DFIALicenseLineSerializer ,DFIALicenseListSerializer
from accounts.permissions import IsAdminUser , IsFactoryUser , IsManagerUser
from accounts.permissions import IsAdminUser, IsManagerUser


class AdvanceLicenseHeadersListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated, IsAdminUser | IsManagerUser]
    queryset = AdvanceLicenseHeaders.objects.all()
    serializer_class = AdvanceLicenseHeaderCreateSerialzer


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
    
    
        
class AdvanceLicenseLinesInsights(APIView):
    def get(self, request, pk):
        insights = AdvanceLicenseLines.objects.filter(license_no=pk).aggregate(
            total_boe_value_usd = Sum('boe_value_usd'),
            total_sb_value_usd = Sum('sb_value_usd'),
            total_balance = Sum('balance'),
            total_import_in_mts = Sum('import_in_mts'),
            total_export_in_mts = Sum('export_in_mts')
        )
        
        return Response(insights)
    
    

class DFIALicenseHeaderCreateView(generics.CreateAPIView):
    queryset = DFIALicenseHeader.objects.all()
    serializer_class = DFIALicenseheaderCreateSerializer
    permission_classes = [IsAuthenticated, IsAdminUser | IsManagerUser]

class DFIALicenseHeaderListView(generics.ListAPIView):
    queryset = DFIALicenseHeader.objects.all()
    serializer_class = DFIALicenseListSerializer
    permission_classes = [IsAuthenticated, IsAdminUser | IsManagerUser]

class DFIALicenseHeaderRetrieveUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    queryset = DFIALicenseHeader.objects.all()
    serializer_class = DFIALicenseListSerializer
    permission_classes = [IsAuthenticated, IsAdminUser | IsManagerUser]
    lookup_field = 'file_no'
    

    
    
    

class DFIALicenseLinesCreateView(generics.CreateAPIView):
    queryset = DFIALicenseLines.objects.all()
    serializer_class = DFIALicenseLineSerializer  # ← fixed
    permission_classes = [IsAuthenticated & (IsManagerUser | IsAdminUser)]  # ← also 'classes' not 'class'

class DFIALicenseLinesListView(generics.ListAPIView):
    queryset = DFIALicenseLines.objects.all()
    serializer_class = DFIALicenseLineSerializer  # ← fixed
    permission_classes = [IsAuthenticated & (IsManagerUser | IsAdminUser)]  # ← also 'classes' not 'class'
    
class DFIALinesInsightView(APIView):
    def get(self, request, pk):
        insights = DFIALicenseLines.objects.filter(license_no=pk).aggregate(
            total_balance=Sum('balance'),
            total_to_be_imported=Sum('to_be_imported_in_mts'),
            total_exported_in_mts=Sum('exported_in_mts'),
            total_sb_value_inr=Sum('sb_value_inr'),
        )

        return Response(insights)

class DFIALicenseLinesRetrieveUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    queryset = DFIALicenseLines.objects.all()
    serializer_class = DFIALicenseLineSerializer
    permission_classes = [IsAuthenticated, IsAdminUser | IsManagerUser]
    lookup_field = 'id'
    
    
    

    
    


    