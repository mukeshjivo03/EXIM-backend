from django.urls import path
from .views import StockStatusListCreateView , StockStatusUpdateRetrieveDeleteView , StockUpdateLogListView , StockStatusInsights , StockStatusSummary

urlpatterns = [
    path('' , StockStatusListCreateView.as_view()),
    path('<int:id>/' , StockStatusUpdateRetrieveDeleteView.as_view()),
    path('stock-logs/' , StockUpdateLogListView.as_view()),
    path('stock-insights/' , StockStatusInsights.as_view()),
    path('stock-summary/' , StockStatusSummary.as_view())
]