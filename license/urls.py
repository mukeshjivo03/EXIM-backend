from django.urls import path
from .views import AdvanceLicenseHeadersListCreateView , AdvanceLicenseLinesListCreateView , AdvanceLicenseRetrieveDeleteView , DFIALicenseHeaderListCreateView , DFIALicenseLinesListCreateView , DFIALicenseHeaderRetrieveUpdateDeleteView




urlpatterns = [
    path('advance-license-headers/', AdvanceLicenseHeadersListCreateView.as_view(), name='advance-license-headers-list-create'),
    path('advance-license-lines/', AdvanceLicenseLinesListCreateView.as_view(), name='advance-license-lines-list-create'),
    path('advance-license-header/<str:license_no>/', AdvanceLicenseRetrieveDeleteView.as_view(), name='advance-license-retrieve-delete'),
    path('dfia-license-header/', DFIALicenseHeaderListCreateView.as_view(), name='dfia-license-header-list-create'),
    path('dfia-license-lines/' , DFIALicenseLinesListCreateView.as_view() , name = 'dfia-license-lines-list-create'),
    path('dfia-license-header/<str:file_no>/', DFIALicenseHeaderRetrieveUpdateDeleteView.as_view(), name='dfia-license-retrieve-update-delete')
]
 