from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import generics
from django.db.models import Sum, Count, Avg
from decimal import Decimal

from .services.services import PartyServices, ProductServices , POService , BalanceSheetService

from accounts.permissions import IsAdminUser , IsManagerUser , IsFactoryUser
from .serializers import RMProductSerializer, FGProductSerializer , PartySerializer , SyncLogSerializer, DomesticContractSerializer
from .models import RMProducts , FGProducts , Party , syncLogs, DomesticContracts

      
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
        queryset = self.get_queryset().exclude(total_qty=0)

        variety = request.query_params.getlist('variety')
        if variety:
            queryset = queryset.filter(u_variety__in=variety)

        serializer = self.get_serializer(queryset, many=True)

        return Response({
            'count' : queryset.count(),
            'items' : serializer.data
        })


class RMProductSummaryView(APIView):

    def get(self, request):
        queryset = RMProducts.objects.exclude(total_qty=0)

        variety = request.query_params.getlist('variety')
        if variety:
            queryset = queryset.filter(u_variety__in=variety)

        summary = queryset.aggregate(
            total_count=Count('id'),
            total_qty=Sum('total_qty'),
            avg_rate=Avg('rate'),
            total_trans_value=Sum('total_trans_value'),
        )

        return Response({
            'summary': {
                'total_count': summary['total_count'] or 0,
                'total_qty': summary['total_qty'] or Decimal('0.00'),
                'avg_rate': round(summary['avg_rate'], 2) if summary['avg_rate'] else Decimal('0.00'),
                'total_trans_value': summary['total_trans_value'] or Decimal('0.00'),
            }
        })


class RMProductVarietyListView(APIView):

    def get(self, request):
        varieties = RMProducts.objects.values_list('u_variety', flat=True).distinct().order_by('u_variety')
        return Response({
            'varieties': [v for v in varieties if v]
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
    
    
class syncPOView(APIView):
    
    def get(self, request):
        result = POService().syncPOs()
        return Response({"records_synced": result})
    

class syncSinglePOView(APIView):
    
    def get(self, request, grpo_no):
        result = POService().syncPO(grpo_no)
        return Response({"po_details": result})
    
    
class DomesticContactListView(generics.ListAPIView):
    permission_classes = [IsAdminUser]
    
    queryset = DomesticContracts.objects.all()
    serializer_class = DomesticContractSerializer
    
class DomesticContractRetrieveUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAdminUser]
    
    queryset = DomesticContracts.objects.all()
    serializer_class = DomesticContractSerializer
    lookup_field = 'id'
    
    
class syncBalanceSheet(APIView):
    
    def get(self, request):
        result = BalanceSheetService().syncBalanceSheet()
        return Response({"balance_sheet": result})
    
    

                                    