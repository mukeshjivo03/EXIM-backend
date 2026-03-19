from django.urls import path
from .views import DomesticReportListView

urlpatterns = [
    path('all/' , DomesticReportListView.as_view())
]