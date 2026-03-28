from django.urls import path 
from .views import PriceFetchView , DailyPriceTrend , DailyPriceListView , DailyPriceRangeView


urlpatterns = [
    path('fetch/' , PriceFetchView.as_view()),
    path('trends/', DailyPriceTrend.as_view()),
    path('db-list/' , DailyPriceListView.as_view()),
    path('range/', DailyPriceRangeView.as_view()),

]