from rest_framework import generics


from .serializers import DomesticReportSerializer
from .models import DomesticReports


class DomesticReportListView(generics.ListAPIView):
    queryset = DomesticReports.objects.all()
    serializer_class = DomesticReportSerializer
    