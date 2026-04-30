from django.urls import path
from .views import StockStatusListCreateView, DebitEntryInsights , StockChangeSessionListView , StockStatusUpdateRetrieveDeleteView , StockUpdateLogListView , StockStatusInsights , StockStatusSummary, StockDashboard, OutsideFactoryStock , GetUniqueRM , GetStockEntrybyRM , ArriveBatch , Dispatch , MoveView , VehicleReport , OpeningStock , DebitEntryListView 







urlpatterns = [
    path('' , StockStatusListCreateView.as_view()),
    path('<int:id>/' , StockStatusUpdateRetrieveDeleteView.as_view()),
    path('stock-logs/', StockChangeSessionListView.as_view()),
    # path('stock-logs/' , StockUpdateLogListView.as_view()),
    
    
    path('debit-entries/', DebitEntryListView.as_view()),
    path('debit-insights/', DebitEntryInsights.as_view()),
    path('opening-stock/' , OpeningStock.as_view(   )),
    path('stock-insights/' , StockStatusInsights.as_view()),
    path('stock-summary/' , StockStatusSummary.as_view()),
    path('stock-dashboard/', StockDashboard.as_view()),
    path('out/' , OutsideFactoryStock.as_view()),
    path('get-unique-rm/' , GetUniqueRM.as_view()),
    path('get-stock-entry-by-rm/', GetStockEntrybyRM.as_view()),
    path('arrive-batch/', ArriveBatch.as_view()),
    path('dispatch/', Dispatch.as_view()),
    path('move/', MoveView.as_view()),
    path('vehicle-report/', VehicleReport.as_view()),
]