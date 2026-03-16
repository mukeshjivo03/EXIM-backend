from django.urls import path
from .views import TankItemViews , TankItemListCreateView , TankItemColorUpdateView , TankDataView, TankDataListCrateView , TankCapacityUpdateView , TankDataSummary , TankItemWiseSummary , TankCapacityInsights ,TankRateBreakdownView , TankInwardView , TankOutwardView , TankStatusView , TankLogsView






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
    path('<str:tank_code>/layers/', TankStatusView.as_view()),
    path('<str:tank_code>/logs/', TankLogsView.as_view()),
 
    # Keep this last — catch-all for tank_code
    path('<str:tank_code>/', TankDataView.as_view()),
]

  