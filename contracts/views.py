from rest_framework import generics


from .serializers import DomesticReportSerializer , ContractSerializer , LoadingSerializer, FreightSerializer
from .models import DomesticReports
from accounts.permissions import IsAdminUser , IsManagerUser


class DomesticReportListView(generics.ListAPIView):
    permission_classes = [IsAdminUser | IsManagerUser]
    
    queryset = DomesticReports.objects.filter()
    serializer_class = DomesticReportSerializer

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
    queryset = DomesticReports.objects.all()
    serializer_class = FreightSerializer
    lookup_field = 'id'
    
class ContractGetView(generics.RetrieveAPIView):
    queryset = DomesticReports.objects.all()
    serializer_class = DomesticReportSerializer
    lookup_field = 'id'


    