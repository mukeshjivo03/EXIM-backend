from django.urls import path
from .views import TankItemViews , TankItemListCreateView , TankItemColorUpdateView , TankDataView, TankDataListCrateView , TankCapacityUpdateView





urlpatterns = [
    path('', TankDataListCrateView.as_view()),
    path('items/' , TankItemListCreateView.as_view()),
    path('<str:tank_number>/' , TankDataView.as_view()),
    path('update-capacity/<str:tank_code>/' , TankCapacityUpdateView.as_view()),
    path('item/update-color/<str:tank_item_code>/' , TankItemColorUpdateView.as_view()),
    path('item/<str:tank_item_code>/' , TankItemViews.as_view()),
]

  