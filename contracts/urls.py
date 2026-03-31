from django.urls import path
from .views import DomesticReportListView , ContractPostView , LoadingPostView , FrieghtPostView , ContractGetView , ContractDropdownView



urlpatterns = [
    path('old-contracts/all/' , DomesticReportListView.as_view()),
    path('dc/contract/create/' , ContractPostView.as_view()),
    path('dc/loading/create/<int:id>/' , LoadingPostView.as_view()),
    path('dc/freight/create/<int:id>/' , FrieghtPostView.as_view()),
    path('dc/<int:id>/' , ContractGetView.as_view()),
    path('dc/dropdown/' , ContractDropdownView.as_view())

]