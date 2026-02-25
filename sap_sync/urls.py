from django.contrib import admin
from django.urls import path 
from .views import  syncPartyView , syncProductsView , syncSingleProductView , ProductGetandDeleteView , ProductListView , PartyGetandDeleteView , PartyListView , SyncLogListView



urlpatterns = [
    path('sap_sync/item/<str:itemCode>/' , syncSingleProductView.as_view()),
    path('sap_sync/party/<str:cardCode>/' , syncPartyView.as_view()),
    path('sap_sync/items/' , syncProductsView.as_view()),

    
    path('item/<str:item_code>/' , ProductGetandDeleteView.as_view()),
    path('items/' , ProductListView.as_view()),
    path('party/<str:card_code>/',PartyGetandDeleteView.as_view()),
    path('parties/',PartyListView.as_view()),
    path('sync_logs/' , SyncLogListView.as_view())

]