from rest_framework import generics


from .serializers import DomesticReportSerializer
from .models import DomesticReports
from accounts.permissions import IsAdminUser , IsManagerUser


class DomesticReportListView(generics.ListAPIView):
    permission_classes = [IsAdminUser | IsManagerUser]
    
    queryset = DomesticReports.objects.all()
    serializer_class = DomesticReportSerializer
    