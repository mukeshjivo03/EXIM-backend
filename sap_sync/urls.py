from django.contrib import admin
from django.urls import path 
from .views import  syncPartyView , syncProuctsView , syncSingleProductView , ProductGetandDeleteView , ProductListView , PartyGetandDeleteView , PartyListView



urlpatterns = [
    path('sap_sync/items/' , syncProuctsView.as_view()),
    path('sap_sync/item/<str:itemCode>/' , syncSingleProductView.as_view()),
    path('sap_sync/party/<str:cardCode>/' , syncPartyView.as_view()),
    
    
    path('item/<str:item_code>/' , ProductGetandDeleteView.as_view()),
    path('items/' , ProductListView.as_view()),
    path('party/<str:card_code>/',PartyGetandDeleteView.as_view()),
    path('parties/',PartyListView.as_view())

]