from django.urls import path 
from .views import PriceFetchView , DailyPriceTrend , DailyPriceListView , DailyPriceRangeView , JivoRatesFetch , JivoRatesWithRange , GetHighestLowestByMonth





urlpatterns = [
    path('daily-price/fetch/' , PriceFetchView.as_view()),
    path('daily-price/trends/', DailyPriceTrend.as_view()),
    path('daily-price/db-list/' , DailyPriceListView.as_view()),
    path('daily-price/range/', DailyPriceRangeView.as_view()),
    path('daily-price/highest-lowest/', GetHighestLowestByMonth.as_view()),
    
    path('jivo-rate/fetch/' , JivoRatesFetch.as_view()),
    path('jivo-rate/range/', JivoRatesWithRange.as_view()),
]