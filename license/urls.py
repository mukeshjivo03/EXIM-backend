from django.urls import path
from .views import AdvanceLicenseHeadersListCreateView , AdvanceLicenseImportListCreateView ,AdvanceLicenseImportLinesRetrieveUpdateDeleteView,AdvanceLicenseExportListCreateView,AdvanceLicenseExportLinesRetrieveUpdateDeleteView,AdvanceLicenseHeaderRetrieveUpdateDeleteView ,DFIALicenseHeaderCreateView , DFIALicenseImportLinesListView , DFIALicenseImportLinesCreateView,DFIALicenseImportLinesRetrieveUpdateDeleteView , DFIALicenseExportLinesListView , DFIALicenseExportLinesCreateView,DFIALicenseExportLinesRetrieveUpdateDeleteView  ,DFIALicenseHeaderListView, DFIALicenseHeaderRetrieveUpdateDeleteView  , AdvanceLicenseImportDropdownView




urlpatterns = [
    path('advance-license-headers/', AdvanceLicenseHeadersListCreateView.as_view(), name='advance-license-headers-list-create'),
    path('advance-license-header/<str:license_no>/', AdvanceLicenseHeaderRetrieveUpdateDeleteView.as_view(), name='advance-license-retrieve-delete'),

    path('advance-license-import-lines/', AdvanceLicenseImportListCreateView.as_view(), name='advance-license-lines-list-create'),
    path('advance-license-import-lines/<int:id>/', AdvanceLicenseImportLinesRetrieveUpdateDeleteView.as_view(), name='advance-license-lines-retrieve-update-delete'),
    
    path('advance-license-export-lines/', AdvanceLicenseExportListCreateView.as_view(), name='advance-license-lines-list-create'),
    path('advance-license-export-lines/<int:id>/', AdvanceLicenseExportLinesRetrieveUpdateDeleteView.as_view(), name='advance-license-lines-retrieve-update-delete'),
    
    path('advance-license-import-lines/dropdown/', AdvanceLicenseImportDropdownView.as_view(), name='advance-license-import-dropdown'),
    
    # path('advance-license-lines/insight/<str:pk>/', AdvanceLicenseLinesInsights.as_view(), name='advance-license-lines-insight'),
    
    path('dfia-license-header/create/', DFIALicenseHeaderCreateView.as_view(), name='dfia-license-header-list-create'),
    path('dfia-license-header/list/' , DFIALicenseHeaderListView.as_view() , name = 'dfia-license-lines-list-create'),
    path('dfia-license-header/<str:file_no>/', DFIALicenseHeaderRetrieveUpdateDeleteView.as_view(), name='dfia-license-retrieve-update-delete'),
    
    path('dfia-license-import-lines/create/' , DFIALicenseImportLinesCreateView.as_view() , name = 'dfia-license-lines-list-create'),
    path('dfia-license-import-lines/list/' , DFIALicenseImportLinesListView.as_view() , name = 'dfia-license-lines-list-create'),
    path('dfia-license-import-lines/<int:id>/' , DFIALicenseImportLinesRetrieveUpdateDeleteView.as_view() , name = 'dfia-license-lines-list-create'),
    
    
    
    path('dfia-license-export-lines/create/' , DFIALicenseExportLinesCreateView.as_view() , name = 'dfia-license-lines-list-create'),
    path('dfia-license-export-lines/list/' , DFIALicenseExportLinesListView.as_view() , name = 'dfia-license-lines-list-create'),
    path('dfia-license-export-lines/<int:id>/' , DFIALicenseExportLinesRetrieveUpdateDeleteView.as_view() , name = 'dfia-license-lines-list-create'),
    
    
    # path('dfia-license-lines/insight/<str:pk>/' , DFIALinesInsightView.as_view() , name = 'dfia-license-lines-isngiht')

]
    