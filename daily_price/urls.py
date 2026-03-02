from django.urls import path 
from .views import PriceFetchView

urlpatterns = [
    path('fetch/' , PriceFetchView.as_view())
]