from django.urls import path
from .views import TankItemViews , TankItemListCreateView , TankItemColorUpdateView , TankDataView, TankDataListCrateView , TankCapacityUpdateView , TankDataSummary , TankItemWiseSummary , TankCapacityInsights





urlpatterns = [
    path('', TankDataListCrateView.as_view()),
    path('items/' , TankItemListCreateView.as_view()),
    path('tank-summary/' , TankDataSummary.as_view()),
    path('capacity-insights/' , TankCapacityInsights.as_view(), name='tank-capacity-insights'),
    path('item-wise-summary/' , TankItemWiseSummary.as_view()),
    path('update-capacity/<str:tank_code>/' , TankCapacityUpdateView.as_view()),
    path('item/update-color/<str:tank_item_code>/' , TankItemColorUpdateView.as_view()),
    path('item/<str:tank_item_code>/' , TankItemViews.as_view()),
    path('<str:tank_code>/' , TankDataView.as_view()),
]

  