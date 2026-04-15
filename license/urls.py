from django.urls import path
from .views import AdvanceLicenseHeadersListCreateView , AdvanceLicenseImportListCreateView ,AdvanceLicenseImportLinesRetrieveUpdateDeleteView,AdvanceLicenseExportListCreateView,AdvanceLicenseExportLinesRetrieveUpdateDeleteView,AdvanceLicenseHeaderRetrieveUpdateDeleteView ,DFIALicenseHeaderCreateView , DFIALicenseLinesListView , DFIALicenseLinesCreateView,DFIALicenseLinesRetrieveUpdateDeleteView  ,DFIALicenseHeaderListView, DFIALicenseHeaderRetrieveUpdateDeleteView ,DFIALinesInsightView 




urlpatterns = [
    path('advance-license-headers/', AdvanceLicenseHeadersListCreateView.as_view(), name='advance-license-headers-list-create'),
    path('advance-license-header/<str:license_no>/', AdvanceLicenseHeaderRetrieveUpdateDeleteView.as_view(), name='advance-license-retrieve-delete'),

    path('advance-license-import-lines/', AdvanceLicenseImportListCreateView.as_view(), name='advance-license-lines-list-create'),
    path('advance-license-import-lines/<int:id>/', AdvanceLicenseImportLinesRetrieveUpdateDeleteView.as_view(), name='advance-license-lines-retrieve-update-delete'),
    
    path('advance-license-export-lines/', AdvanceLicenseExportListCreateView.as_view(), name='advance-license-lines-list-create'),
    path('advance-license-export-lines/<int:id>/', AdvanceLicenseExportLinesRetrieveUpdateDeleteView.as_view(), name='advance-license-lines-retrieve-update-delete'),
    
    
    
    # path('advance-license-lines/insight/<str:pk>/', AdvanceLicenseLinesInsights.as_view(), name='advance-license-lines-insight'),
    
    path('dfia-license-header/create/', DFIALicenseHeaderCreateView.as_view(), name='dfia-license-header-list-create'),
    path('dfia-license-header/list/' , DFIALicenseHeaderListView.as_view() , name = 'dfia-license-lines-list-create'),
    path('dfia-license-header/<str:file_no>/', DFIALicenseHeaderRetrieveUpdateDeleteView.as_view(), name='dfia-license-retrieve-update-delete'),
    
    path('dfia-license-lines/create/' , DFIALicenseLinesCreateView.as_view() , name = 'dfia-license-lines-list-create'),
    path('dfia-license-lines/list/' , DFIALicenseLinesListView.as_view() , name = 'dfia-license-lines-list-create'),
    path('dfia-license-lines/<int:id>/' , DFIALicenseLinesRetrieveUpdateDeleteView.as_view() , name = 'dfia-license-lines-list-create'),
    path('dfia-license-lines/insight/<str:pk>/' , DFIALinesInsightView.as_view() , name = 'dfia-license-lines-isngiht')

]
    