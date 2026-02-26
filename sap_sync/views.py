from rest_framework.views import APIView
from rest_framework.response import Response 
from rest_framework import generics

from .services.services import PartyServices, ProductServices
from accounts.permissions import IsAdminUser , IsManagerUser , IsFactoryUser
from .serializers import RMProductSerializer, FGProductSerializer , PartySerializer , SyncLogSerializer
from .models import RMProducts , FGProducts , Party , syncLogs

      
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

        
class syncRMProductsView(APIView):
    permission_classes = [IsAdminUser]
    def get(self, request):
        try:
            result = ProductServices().syncRMProducts()
            serializer =  RMProductSerializer(RMProducts.objects.all() , many=True)
            
            return Response({'success': True , 'Items_processed' : result, 'Items': serializer.data})
            
        except Exception as e:
            return Response({'success': False, 'error': str(e)}, status=500)
        
class syncFGProductsView(APIView):
    permission_classes = [IsAdminUser]
    def get(self, request):
        try:
            result = ProductServices().syncFGProducts()
            serializer =  FGProductSerializer(FGProducts.objects.all() , many=True)
            
            return Response({'success': True , 'Items_processed' : result, 'Items': serializer.data})
            
        except Exception as e:
            return Response({'success': False, 'error': str(e)}, status=500)
        
        
class syncSingleRMProductView(APIView):
    permission_classes = [IsAdminUser]
    def get(self, request, itemCode):
        try:
            result = ProductServices().syncRMProduct(itemCode)
            serializer = RMProductSerializer(result)
            return Response({'status': 'success', 'item_code': result.item_code,'synced_item' : serializer.data})
            
        except Exception as e:
            return Response({'success': False, 'error': str(e)}, status=500)
        
class syncSingleFGProductView(APIView):
    permission_classes = [IsAdminUser]
    def get(self, request, itemCode):
        try:
            result = ProductServices().syncFGProduct(itemCode)
            serializer = FGProductSerializer(result)
            return Response({'status': 'success', 'item_code': result.item_code,'synced_item' : serializer.data})
            
        except Exception as e:
            return Response({'success': False, 'error': str(e)}, status=500)
        
        
        
# Model Views 
        
class RMProductGetandDeleteView(generics.RetrieveDestroyAPIView):
    permission_classes = [IsAdminUser]
    
    queryset = RMProducts.objects.all()
    serializer_class = RMProductSerializer 
    lookup_field = 'item_code'
    
    
    
class RMProductListView(generics.ListAPIView):
    permission_class = [IsAdminUser]
    
    queryset = RMProducts.objects.all()
    serializer_class = RMProductSerializer
    
    def list(self, request):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        
        return Response({
            'count' : queryset.count(),
            'items' : serializer.data
        })
        
class FGProductGetandDeleteView(generics.RetrieveDestroyAPIView):
    permission_classes = [IsAdminUser]
    
    queryset = FGProducts.objects.all()
    serializer_class = FGProductSerializer 
    lookup_field = 'item_code'
    
    
    
class FGProductListView(generics.ListAPIView):
    permission_class = [IsAdminUser]
    
    queryset = FGProducts.objects.all()
    serializer_class = FGProductSerializer
    
    def list(self, request):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        
        return Response({
            'count' : queryset.count(),
            'items' : serializer.data
        })
    
class PartyGetandDeleteView(generics.RetrieveDestroyAPIView):
    permission_class = [IsAdminUser]
    
    queryset = Party.objects.all()
    serializer_class = PartySerializer
    lookup_field = 'card_code'
    

class PartyListView(generics.ListAPIView):
    permission_class = [IsAdminUser]
    
    queryset = Party.objects.all()
    serializer_class =  PartySerializer
    
    def list(self, request):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)

        return Response({
            'count' : queryset.count(),
            'parties' : serializer.data
        })    
    
class SyncLogListView(generics.ListAPIView):
    permission_class = [IsAdminUser]
    
    queryset = syncLogs.objects.all()
    serializer_class = SyncLogSerializer