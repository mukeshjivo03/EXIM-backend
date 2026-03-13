from django.urls import path
from .views import AdvanceLicenseHeadersListCreateView , AdvanceLicenseLinesListCreateView , AdvanceLicenseHeaderRetrieveUpdateDeleteView , DFIALicenseHeaderCreateView , DFIALicenseLinesListCreateView  ,DFIALicenseHeaderListView, DFIALicenseHeaderRetrieveUpdateDeleteView




urlpatterns = [
    path('advance-license-headers/', AdvanceLicenseHeadersListCreateView.as_view(), name='advance-license-headers-list-create'),
    path('advance-license-lines/', AdvanceLicenseLinesListCreateView.as_view(), name='advance-license-lines-list-create'),
    
    path('advance-license-header/<str:license_no>/', AdvanceLicenseHeaderRetrieveUpdateDeleteView.as_view(), name='advance-license-retrieve-delete'),
    path('dfia-license-header/create/', DFIALicenseHeaderCreateView.as_view(), name='dfia-license-header-list-create'),
    
    path('dfia-license-lines/' , DFIALicenseHeaderCreateView.as_view() , name = 'dfia-license-lines-list-create'),
    path('dfia-license-header/list/' , DFIALicenseHeaderListView.as_view() , name = 'dfia-license-lines-list-create'),
    path('dfia-license-header/<str:file_no>/', DFIALicenseHeaderRetrieveUpdateDeleteView.as_view(), name='dfia-license-retrieve-update-delete')
]
    