from django.urls import path 
from .views import PriceFetchView , DailyPriceTrend

urlpatterns = [
    path('fetch/' , PriceFetchView.as_view()),
    path('trends/', DailyPriceTrend.as_view())
]