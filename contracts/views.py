from rest_framework import generics
from datetime import date
from rest_framework.views import APIView
from rest_framework.response import Response

from .serializers import DomesticReportSerializer , ContractSerializer , LoadingSerializer, FreightSerializer , ContractDropdownSerializer
from .models import DomesticReports
from accounts.permissions import IsAdminUser , IsManagerUser


class DomesticReportListView(APIView):
    def get(self,request):
        year = request.query_params.get('year')
        user_year = int(year)
        
        start_date = date(user_year , 4 , 1)
        end_date = date(user_year+ 1 , 3 , 31)
        
        data = DomesticReports.objects.filter(po_date__range=[start_date , end_date])
        serializer = DomesticReportSerializer(data , many=True)
        return Response(serializer.data)
        
class ContractPostView(generics.CreateAPIView):
    permission_classes = [IsAdminUser | IsManagerUser]
    queryset = DomesticReports.objects.all()
    serializer_class = ContractSerializer   

class LoadingPostView(generics.UpdateAPIView):
    permission_classes = [IsAdminUser | IsManagerUser]
    queryset = DomesticReports.objects.all()
    serializer_class = LoadingSerializer
    lookup_field = 'id'
    
class FrieghtPostView(generics.UpdateAPIView):
    permission_classes = [IsAdminUser | IsManagerUser]
    
    queryset = DomesticReports.objects.all()
    serializer_class = FreightSerializer
    lookup_field = 'id'
    
class ContractGetView(generics.RetrieveAPIView):
    permission_classes = [IsAdminUser | IsManagerUser]
    
    queryset = DomesticReports.objects.all()
    serializer_class = DomesticReportSerializer
    lookup_field = 'id'

class ContractDropdownView(generics.ListAPIView):
    permission_classes = [IsAdminUser | IsManagerUser]
    
    queryset = DomesticReports.objects.all().order_by('-created_at')
    serializer_class = ContractDropdownSerializer
    

    