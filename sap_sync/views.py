from rest_framework.views import APIView
from rest_framework.response import Response 
from rest_framework import generics

from .services.services import PartyServices, ProductServices
from accounts.permissions import IsAdminUser , IsManagerUser , IsFactoryUser
from .serializers import ProductSerializer , PartySerializer , SyncLogSerializer
from .models import Products , Party , syncLogs

      
# Sync Views
      
class syncPartyView(APIView):
    
    permission_classes = [IsAdminUser]
    def get(self, request, cardCode):
        try:
            party_obj = PartyServices().syncParty(cardCode)
            serialier = PartySerializer(party_obj)
            
            return Response({'success': True, 'party_processed': party_obj.card_code , 'party' : serialier.data})
            
        except Exception as e:
            # Add status=500 for proper error handling
            return Response({'success': False, 'error': str(e)}, status=500)

        
class syncProuctsView(APIView):
    permission_classes = [IsAdminUser]
    def get(self, request):
        try:
            result = ProductServices().syncProducts()
            serializer =  ProductSerializer(Products.objects.all() , many=True)
            
            return Response({'success': True , 'Items_processed' : result, 'Items': serializer.data})
            
        except Exception as e:
            return Response({'success': False, 'error': str(e)}, status=500)
        
        
class syncSingleProductView(APIView):
    permission_classes = [IsAdminUser]
    def get(self, request, itemCode):
        try:
            result = ProductServices().syncProduct(itemCode)
            serializer = ProductSerializer(result)
            return Response({'status': 'success', 'item_code': result.item_code,'synced_item' : serializer.data})
            
        except Exception as e:
            return Response({'success': False, 'error': str(e)}, status=500)
        
        
        
# Model Views 
        
class ProductGetandDeleteView(generics.RetrieveDestroyAPIView):
    permission_classes = [IsAdminUser]
    
    queryset = Products.objects.all()
    serializer_class = ProductSerializer 
    lookup_field = 'item_code'
    
    
    
class ProductListView(generics.ListAPIView):
    permission_class = [IsAdminUser]
    
    queryset = Products.objects.all()
    serializer_class = ProductSerializer
    
    
class PartyGetandDeleteView(generics.RetrieveDestroyAPIView):
    permission_class = [IsAdminUser]
    
    queryset = Party.objects.all()
    serializer_class = PartySerializer
    lookup_field = 'card_code'
    

class PartyListView(generics.ListAPIView):
    permission_class = [IsAdminUser]
    
    queryset = Party.objects.all()
    serializer_class =  PartySerializer
    