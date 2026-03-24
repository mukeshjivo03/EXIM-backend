from django.urls import path
from .views import TankItemViews , TankItemListCreateView , TankItemColorUpdateView , TankDataView, TankDataListCrateView , TankCapacityUpdateView , TankDataSummary , TankItemWiseSummary , TankCapacityInsights ,TankRateBreakdownView , TankInwardView , TankOutwardView , TankTransferView , TankStatusView , TankLogsView , TankConsumptionView , TankLogView , EmptyorSameTanks








urlpatterns = [
    path('', TankDataListCrateView.as_view()),
    path('items/' , TankItemListCreateView.as_view()),
    path('tank-summary/' , TankDataSummary.as_view()),
    path('capacity-insights/' , TankCapacityInsights.as_view(), name='tank-capacity-insights'),
    path('item-wise-summary/' , TankItemWiseSummary.as_view()),
    path('tank-rates/', TankRateBreakdownView.as_view()),
    path('update-capacity/<str:tank_code>/' , TankCapacityUpdateView.as_view()),
    path('item/update-color/<str:tank_item_code>/' , TankItemColorUpdateView.as_view()),
    path('item/<str:tank_item_code>/' , TankItemViews.as_view()),
    
    path('inward/', TankInwardView.as_view()),
    path('outward/', TankOutwardView.as_view()),
    path('transfer/', TankTransferView.as_view()),
    path('layers/<str:tank_code>/', TankStatusView.as_view()),
    path('logs/<str:tank_code>/', TankLogsView.as_view()),
    path('consumption/', TankConsumptionView.as_view()),
    path('log/', TankLogView.as_view()),
    path('get-same-tanks/', EmptyorSameTanks.as_view()),
    
    # Keep this last — catch-all for tank_code
    path('<str:tank_code>/', TankDataView.as_view()),
]

  