from django.urls import path
from .views import DomesticReportListView , ContractPostView , LoadingPostView

urlpatterns = [
    path('old-contracts/all/' , DomesticReportListView.as_view()),
    path('dc/contract/create/' , ContractPostView.as_view()),
    path('dc/loading/create/<int:id>/' , LoadingPostView.as_view()),
]