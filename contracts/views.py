from rest_framework import generics
from datetime import date
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q

from .serializers import DomesticReportSerializer , ContractSerializer , LoadingSerializer, FreightSerializer , ContractDropdownSerializer
from .models import DomesticReports
from accounts.permissions import HasAppPermission


class DomesticReportListView(APIView):
    def get_permissions(self):
        return [IsAuthenticated() , HasAppPermission('contracts.view_domesticreports')]
    def get(self,request):
        year = request.query_params.get('year')
        user_year = int(year)
        
        # start_date = date(user_year , 4 , 1)
        
        start_date = date(user_year , 2 , 1)
        end_date = date(user_year+ 1 , 3 , 31)
        print(start_date , end_date)
        
        # data = DomesticReports.objects.filter(grpo_date__range=[start_date , end_date])
        data = DomesticReports.objects.filter( po_date__range=[start_date, end_date]).order_by('po_date')

        serializer = DomesticReportSerializer(data , many=True)
        return Response(serializer.data)
        
        

class ContractPostView(generics.CreateAPIView):
    def get_permissions(self):
        return [IsAuthenticated() , HasAppPermission('contracts.add_domesticreports')]

    queryset = DomesticReports.objects.all()
    serializer_class = ContractSerializer   
    
class LoadingPostView(generics.UpdateAPIView):
    def get_permissions(self):
        return [IsAuthenticated() , HasAppPermission('contracts.change_domesticreports')]

    queryset = DomesticReports.objects.all()
    serializer_class = LoadingSerializer
    lookup_field = 'id'
    
class FrieghtPostView(generics.UpdateAPIView):
    def get_permissions(self):
        return [IsAuthenticated() , HasAppPermission('contracts.change_domesticreports')]
    
    queryset = DomesticReports.objects.all()
    serializer_class = FreightSerializer
    lookup_field = 'id'
    
class ContractGetView(generics.RetrieveUpdateDestroyAPIView):

    def get_permissions(self):
        if self.request.method == 'DELETE':
            return [IsAuthenticated() , HasAppPermission('contracts.delete_domesticreports')]
        if self.request.method in ['PUT' , 'PATCH']:
            return [IsAuthenticated(), HasAppPermission('contracts.change_domesticreports')] 

        return [IsAuthenticated(), HasAppPermission('contracts.view_domesticreports')]

    
    queryset = DomesticReports.objects.all()
    serializer_class = DomesticReportSerializer
    lookup_field = 'id'

class ContractDropdownView(generics.ListAPIView):
    def get_permissions(self):
        return [IsAuthenticated(), HasAppPermission('contracts.view_domesticreports')]
    
    queryset = DomesticReports.objects.all().order_by('-created_at')
    serializer_class = ContractDropdownSerializer
    


    