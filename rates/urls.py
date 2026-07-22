from django.urls import path
from .views import PackingMarginListCreateView , CommodityMarginListCreateView , MarketRateCreateView , MarketRatesGetView ,PackingMarginRetrieveUpdateDeleteView , MarketRateRetrieveUpdateDeleteView , GetLatestMarketRates,GetBasicRatesView , PackSizeListCreateView , PackSizeRetrieveUpdateDeleteView , GetPackRatesView , GetLatestRateTableView ,CommodityMarginRetrieveUpdateDeleteView


urlpatterns = [
    path('packing/' ,  PackingMarginListCreateView.as_view()),
    path('commodity/' ,  CommodityMarginListCreateView.as_view()),
    path('market-rate/add/' , MarketRateCreateView.as_view()),
    path('market-rate/get/' , MarketRatesGetView.as_view()),
    path('market-rate/latest/' , GetLatestMarketRates.as_view()),
    path('basic-rate/' , GetBasicRatesView.as_view()),

    path('pack-size/' , PackSizeListCreateView.as_view()),
    path('pack-size/<int:id>/' , PackSizeRetrieveUpdateDeleteView.as_view()),
    path('pack-rate/' , GetPackRatesView.as_view()),
    path('rate-table/latest/' , GetLatestRateTableView.as_view()),

    path('packing/<int:id>/' , PackingMarginRetrieveUpdateDeleteView.as_view()),
    path('market-rate/<int:id>/' , MarketRateRetrieveUpdateDeleteView.as_view()),
    path('commodity/<int:id>/' , CommodityMarginRetrieveUpdateDeleteView.as_view())

]