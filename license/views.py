from django.shortcuts import render
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Sum
from rest_framework.permissions import IsAuthenticated

from .models import AdvanceLicenseHeaders, AdvanceLicenseImportLines , AdvanceLicenseExportLines , DFIALicenseHeader , DFIALicenseExportLines , DFIALicenseImportLines
from .serializers import AdvanceLicenseHeaderSerialzer, AdvanceLicenseImportLine , AdvanceLicenseExportLine , AdvanceLicenseHeaderCreateSerialzer, DFIALicenseheaderCreateSerializer , DFIAImportLines , DFIAExportLines ,DFIALicenseListSerializer
from accounts.permissions import HasAppPermission

class AdvanceLicenseHeadersListCreateView(generics.ListCreateAPIView):
    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated() , HasAppPermission('license.add_advancelicenseheaders')]
        
        return [IsAuthenticated() , HasAppPermission('license.view_advancelicenseheaders')]

    queryset = AdvanceLicenseHeaders.objects.all()
    serializer_class = AdvanceLicenseHeaderCreateSerialzer


class AdvanceLicenseHeaderRetrieveUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    def get_permissions(self):
        if self.request.method == 'DELETE':
            return [IsAuthenticated() , HasAppPermission('license.delete_advancelicenseheaders')]
        if self.request.method in ['PUT' , 'PATCH']:
            return [IsAuthenticated() , HasAppPermission('license.change_advancelicenseheaders')]

        return [IsAuthenticated() , HasAppPermission('license.view_advancelicenseheaders')]


    queryset = AdvanceLicenseHeaders.objects.all()
    serializer_class = AdvanceLicenseHeaderCreateSerialzer
    lookup_field = 'license_no'
        
    
class AdvanceLicenseImportListCreateView(generics.ListCreateAPIView):
    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated() , HasAppPermission('license.add_advancelicenseimportlines')]
        
        return [IsAuthenticated() , HasAppPermission('license.view_advancelicenseimportlines')]
    queryset = AdvanceLicenseImportLines.objects.all()
    serializer_class = AdvanceLicenseImportLine
    
class AdvanceLicenseImportLinesRetrieveUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    def get_permissions(self):
        if self.request.method == 'DELETE':
            return [IsAuthenticated() , HasAppPermission('license.delete_advancelicenseimportlines')]
        if self.request.method in ['PUT' , 'PATCH']:
            return [IsAuthenticated() , HasAppPermission('license.change_advancelicenseimportlines')]

        return [IsAuthenticated() , HasAppPermission('license.view_advancelicenseimportlines')]

    queryset = AdvanceLicenseImportLines.objects.all()
    serializer_class = AdvanceLicenseImportLine
    lookup_field = 'id'
    
    
 
class AdvanceLicenseExportListCreateView(generics.ListCreateAPIView):
    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated() , HasAppPermission('license.add_advancelicenseexportlines')]
        
        return [IsAuthenticated() , HasAppPermission('license.view_advancelicenseexportlines')]
    queryset = AdvanceLicenseExportLines .objects.all()
    serializer_class = AdvanceLicenseExportLine
    
class AdvanceLicenseExportLinesRetrieveUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    def get_permissions(self):
        if self.request.method == 'DELETE':
            return [IsAuthenticated() , HasAppPermission('license.delete_advancelicenseimportlines')]
        if self.request.method in ['PUT' , 'PATCH']:
            return [IsAuthenticated() , HasAppPermission('license.change_advancelicenseimportlines')]

        return [IsAuthenticated() , HasAppPermission('license.view_advancelicenseimport3lines')]

    queryset = AdvanceLicenseExportLines.objects.all()
    serializer_class = AdvanceLicenseExportLine
    lookup_field = 'id'
    
    
        
# class AdvanceLicenseLinesInsights(APIView):
#     def get_permissions(self):
#         return [IsAuthenticated(), HasAppPermission('license.view_line_insights')]
#     def get(self, request, pk):
#         insights = AdvanceLicenseLines.objects.filter(license_no=pk).aggregate(
#             total_boe_value_usd = Sum('boe_value_usd'),
#             total_sb_value_usd = Sum('sb_value_usd'),
#             total_balance = Sum('balance'),
#             total_import_in_mts = Sum('import_in_mts'),
#             total_export_in_mts = Sum('export_in_mts')
#         )
        
#         return Response(insights)
    
    

class DFIALicenseHeaderCreateView(generics.CreateAPIView):
    def get_permissions(self):
        return [IsAuthenticated(), HasAppPermission('license.add_dfialicenseheader')]

    queryset = DFIALicenseHeader.objects.all()
    serializer_class = DFIALicenseheaderCreateSerializer

class DFIALicenseHeaderListView(generics.ListAPIView):
    def get_permissions(self):
        return [IsAuthenticated(), HasAppPermission('license.view_dfialicenseheader')]
    queryset = DFIALicenseHeader.objects.all()
    serializer_class = DFIALicenseListSerializer
    

class DFIALicenseHeaderRetrieveUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    def get_permissions(self):
        if self.request.method == 'DELETE':
            return [IsAuthenticated() , HasAppPermission('license.delete_dfialicenseheader')]
        if self.request.method in ['PUT' , 'PATCH']:
            return [IsAuthenticated() , HasAppPermission('license.change_dfialicenseheader')]

        return [IsAuthenticated() , HasAppPermission('license.view_dfialicenseheader')]

    queryset = DFIALicenseHeader.objects.all()
    serializer_class = DFIALicenseListSerializer
    lookup_field = 'file_no'
    

    
    
    

class DFIALicenseImportLinesCreateView(generics.CreateAPIView):
    def get_permissions(self):
        return  [IsAuthenticated(), HasAppPermission('license.add_dfialicenseimportlines')]
    queryset = DFIALicenseImportLines.objects.all()
    serializer_class = DFIAImportLines  

class DFIALicenseImportLinesListView(generics.ListAPIView):
    def get_permissions(self):
        return  [IsAuthenticated(), HasAppPermission('license.view_dfialicenseimportlines')]
    
    queryset = DFIALicenseImportLines.objects.all()
    serializer_class = DFIAImportLines  
    

class DFIALicenseImportLinesRetrieveUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    def get_permissions(self):
        if self.request.method == 'DELETE':
            return [IsAuthenticated() , HasAppPermission('license.delete_dfialicenseimportlines')]
        if self.request.method in ['PUT' , 'PATCH']:
            return [IsAuthenticated() , HasAppPermission('license.change_dfialicenseimportlines')]

        return [IsAuthenticated() , HasAppPermission('license.view_dfialicenseimportlines')]

    queryset = DFIALicenseImportLines.objects.all()
    serializer_class = DFIAImportLines  
    lookup_field = 'id'
    


class DFIALicenseExportLinesCreateView(generics.CreateAPIView):
    def get_permissions(self):
        return  [IsAuthenticated(), HasAppPermission('license.add_dfialicenseexportlines')]
    queryset = DFIALicenseExportLines.objects.all()
    serializer_class = DFIAExportLines  

class DFIALicenseExportLinesListView(generics.ListAPIView):
    def get_permissions(self):
        return  [IsAuthenticated(), HasAppPermission('license.view_dfialicenseexportlines')]
    
    queryset = DFIALicenseExportLines.objects.all()
    serializer_class = DFIAExportLines 
    

class DFIALicenseExportLinesRetrieveUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    def get_permissions(self):
        if self.request.method == 'DELETE':
            return [IsAuthenticated() , HasAppPermission('license.delete_dfialicenseexportlines')]
        if self.request.method in ['PUT' , 'PATCH']:
            return [IsAuthenticated() , HasAppPermission('license.change_dfialicenseexportlines')]

        return [IsAuthenticated() , HasAppPermission('license.view_dfialicenseexportlines')]

    
    queryset = DFIALicenseExportLines.objects.all()
    serializer_class = DFIAExportLines  
    lookup_field = 'id'
    


    
    


    # class DFIALinesInsightView(APIView):
#     def get_permissions(self):
#         return  [IsAuthenticated(), HasAppPermission('license.view_dfia_line_insights')]

#     def get(self, request, pk):
#         insights = DFIALicenseLines.objects.filter(license_no=pk).aggregate(
#             total_balance=Sum('balance'),
#             total_to_be_imported=Sum('to_be_imported_in_mts'),
#             total_exported_in_mts=Sum('exported_in_mts'),
#             total_sb_value_inr=Sum('sb_value_inr'),
#         )

#         return Response(insights)