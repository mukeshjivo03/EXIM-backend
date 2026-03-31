from django.urls import path
from .views import DomesticReportListView , ContractPostView , LoadingPostView , FrieghtPostView , ContractGetView , ContractDropdownView



urlpatterns = [
    path('' , DomesticReportListView.as_view()),
    path('contract/create/' , ContractPostView.as_view()),
    path('loading/create/<int:id>/' , LoadingPostView.as_view()),
    path('freight/create/<int:id>/' , FrieghtPostView.as_view()),
    path('<int:id>/' , ContractGetView.as_view()),
    path('dropdown/' , ContractDropdownView.as_view())

]