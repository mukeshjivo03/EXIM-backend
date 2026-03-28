from django.urls import path 
from .views import PriceFetchView , DailyPriceTrend , DailyPriceListView , DailyPriceRangeView , JivoRatesFetch , JivoRatesWithRange





urlpatterns = [
    path('daily-price/fetch/' , PriceFetchView.as_view()),
    path('daily-price/trends/', DailyPriceTrend.as_view()),
    path('daily-price/db-list/' , DailyPriceListView.as_view()),
    path('daily-price/range/', DailyPriceRangeView.as_view()),
    path('jivo-rate/fetch' , JivoRatesFetch.as_view()),
    path('jivo-rate/range/', JivoRatesWithRange.as_view()),
]