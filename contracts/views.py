from rest_framework import generics


from .serializers import DomesticReportSerializer
from .models import DomesticReports


# Create your views here.
class DomesticReportListView(generics.ListAPIView):
    queryset = DomesticReports.objects.all()
    serializer_class = DomesticReportSerializer
    