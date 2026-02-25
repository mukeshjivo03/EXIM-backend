from django.urls import path
from .views import TankItemViews , TankItemListCreateView , TankItemColorUpdateView



urlpatterns = [
    path('items/' , TankItemListCreateView.as_view()),
    path('item/update-color/<str:tank_item_code>/' , TankItemColorUpdateView.as_view()),
    path('item/<str:tank_item_code>/' , TankItemViews.as_view()),
]

  