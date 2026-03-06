from django.urls import path
from .views import StockStatusListCreateView , StockStatusUpdateRetrieveDeleteView , StockUpdateLogListView , StockStatusInsights , StockStatusSummary, StockDashboard


urlpatterns = [
    path('' , StockStatusListCreateView.as_view()),
    path('<int:id>/' , StockStatusUpdateRetrieveDeleteView.as_view()),
    path('stock-logs/' , StockUpdateLogListView.as_view()),
    path('stock-insights/' , StockStatusInsights.as_view()),
    path('stock-summary/' , StockStatusSummary.as_view()),
    path('stock-dashboard/', StockDashboard.as_view())
]