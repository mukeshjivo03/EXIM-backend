from django.urls import path
from .views import AdvanceLicenseHeadersListCreateView , AdvanceLicenseLinesListCreateView , AdvanceLicenseRetrieveDeleteView



urlpatterns = [
    path('advance-license-headers/', AdvanceLicenseHeadersListCreateView.as_view(), name='advance-license-headers-list-create'),
    path('advance-license-lines/', AdvanceLicenseLinesListCreateView.as_view(), name='advance-license-lines-list-create'),
    path('advance-license-header/<str:license_no>/', AdvanceLicenseRetrieveDeleteView.as_view(), name='advance-license-retrieve-delete'),
]
 