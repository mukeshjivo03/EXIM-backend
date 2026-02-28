from django.contrib import admin
from django.urls import path 
from .views import  syncPartyView , syncRMProductsView , syncFGProductsView , syncSingleRMProductView, syncSingleFGProductView , RMProductGetandDeleteView , RMProductListView , RMProductSummaryView , RMProductVarietyListView ,FGProductGetandDeleteView , FGProductListView , PartyGetandDeleteView , PartyListView , SyncLogListView



urlpatterns = [
    path('sap_sync/fg/item/<str:itemCode>/' , syncSingleFGProductView.as_view()),
    path('sap_sync/rm/item/<str:itemCode>/' , syncSingleRMProductView.as_view()),
    path('sap_sync/party/<str:cardCode>/' , syncPartyView.as_view()),
    path('sap_sync/rm/items/' , syncRMProductsView.as_view()),
    path('sap_sync/fg/items/' , syncFGProductsView.as_view()),

    
    path('item/rm/<str:item_code>/' , RMProductGetandDeleteView.as_view()),
    path('items/rm/' , RMProductListView.as_view()),
    path('items/rm/summary/' , RMProductSummaryView.as_view()),
    path('items/rm/varieties/' , RMProductVarietyListView.as_view()),
    
    path('item/fg/<str:item_code>/' , FGProductGetandDeleteView.as_view()),
    path('items/fg/' , FGProductListView.as_view()),
    
    path('party/<str:card_code>/',PartyGetandDeleteView.as_view()),
    path('parties/',PartyListView.as_view()),
    path('sync_logs/' , SyncLogListView.as_view())

]