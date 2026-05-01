from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum, Count, Avg , Q
from django.db.models.functions import Round, Coalesce
from decimal import Decimal

from .services.services import PartyServices, ProductServices , POService , BalanceSheetService, GRPOServices , InventoryService , APService
from .services.connections import Queries

from .serializers import RMProductSerializer, FGProductSerializer , PartySerializer , SyncLogSerializer, DomesticContractSerializer
from .models import RMProducts , FGProducts , Party , syncLogs, DomesticContracts
from stock.models import StockStatus
from tank.models import TankData
from accounts.permissions import HasAppPermission
      
# Sync Views
      
class syncPartyView(APIView):
    def get_permissions(self):
        return [IsAuthenticated(), HasAppPermission('sap_sync.sync_party')]
    def get(self, request, cardCode):
        try:
            party_obj = PartyServices().syncParty(cardCode)
            serialier = PartySerializer(party_obj)
            
            return Response({'success': True, 'party_processed': party_obj.card_code , 'party' : serialier.data})
            
        except Exception as e:
            # Add status=500 for proper error handling
            return Response({'success': False, 'error': str(e)}, status=500)

        
class syncRMProductsView(APIView):
    def get_permissions(self):
        return [IsAuthenticated() , HasAppPermission('sap_sync.sync_rm')]

    def get(self, request):
        try:
            result = ProductServices().syncRMProducts()
            serializer =  RMProductSerializer(RMProducts.objects.all() , many=True)
            
            return Response({'success': True , 'Items_processed' : result, 'Items': serializer.data})
            
        except Exception as e:
            return Response({'success': False, 'error': str(e)}, status=500)
        
class syncFGProductsView(APIView):
    def get_permissions(self):
        return [IsAuthenticated() , HasAppPermission('sap_sync.sync_fg')]

    def get(self, request):
        try:
            result = ProductServices().syncFGProducts()
            serializer =  FGProductSerializer(FGProducts.objects.all() , many=True)
            
            return Response({'success': True , 'Items_processed' : result, 'Items': serializer.data})
            
        except Exception as e:
            return Response({'success': False, 'error': str(e)}, status=500)
        
        
class syncSingleRMProductView(APIView):
    def get_permissions(self):
        return [IsAuthenticated() , HasAppPermission('sap_sync.sync_rm')]

    def get(self, request, itemCode):
        try:
            result = ProductServices().syncRMProduct(itemCode)
            serializer = RMProductSerializer(result)
            return Response({'status': 'success', 'item_code': result.item_code,'synced_item' : serializer.data})
            
        except Exception as e:
            return Response({'success': False, 'error': str(e)}, status=500)
        
class syncSingleFGProductView(APIView):
    def get_permissions(self):
        return [IsAuthenticated() , HasAppPermission('sap_sync.sync_fg')]

    def get(self, request, itemCode):
        try:
            result = ProductServices().syncFGProduct(itemCode)
            serializer = FGProductSerializer(result)
            return Response({'status': 'success', 'item_code': result.item_code,'synced_item' : serializer.data})
            
        except Exception as e:
            return Response({'success': False, 'error': str(e)}, status=500)
        
        
        
# Model Views 
        
class RMProductGetandDeleteView(generics.RetrieveDestroyAPIView):
    def get_permissions(self):
        if self.request.method == 'DELETE':
            return [IsAuthenticated() , HasAppPermission('sap_sync.delete_rmproducts')]
        
        return [IsAuthenticated() , HasAppPermission('sap_sync.view_rmproducts')]
        
    queryset = RMProducts.objects.all()
    serializer_class = RMProductSerializer 
    lookup_field = 'item_code'
    
    
    
class RMProductListView(generics.ListAPIView):
    def get_permissions(self):
        return [IsAuthenticated() , HasAppPermission('sap_sync.view_rmproducts')]
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
    def get_permissions(self):
        return [IsAuthenticated() , HasAppPermission('sap_sync.view_rmproducts')]

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
    def get_permissions(self):
        return [IsAuthenticated() , HasAppPermission('sap_sync.view_rmproducts')]

    def get(self, request):
        varieties = RMProducts.objects.values_list('u_variety', flat=True).distinct().order_by('u_variety')
        return Response({
            'varieties': [v for v in varieties if v]
        })
        
class FGProductGetandDeleteView(generics.RetrieveDestroyAPIView):
    def get_permissions(self):
        if self.request.method == 'DELETE':
            return [IsAuthenticated() , HasAppPermission('sap_sync.delete_fgproducts')]
        
        return [IsAuthenticated() , HasAppPermission('sap_sync.view_fgproducts')]
        
    queryset = FGProducts.objects.all()
    serializer_class = FGProductSerializer 
    lookup_field = 'item_code'
    
    
    
class FGProductListView(generics.ListAPIView):
    def get_permissions(self):
        return [IsAuthenticated() , HasAppPermission('sap_sync.view_fgproducts')]

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
    def get_permissions(self):
        if self.request.method == 'DELETE':
            return [IsAuthenticated() , HasAppPermission('sap_sync.delete_party')]
        
        return [IsAuthenticated() , HasAppPermission('sap_sync.view_party')]
        
    queryset = Party.objects.all()
    serializer_class = PartySerializer
    lookup_field = 'card_code'
    

class PartyListView(generics.ListAPIView):
    def get_permissions(self):
        return [IsAuthenticated() , HasAppPermission('sap_sync.view_party')]

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
    def get_permissions(self):
        return [IsAuthenticated() , HasAppPermission('sap_sync.view_synclogs')]

    queryset = syncLogs.objects.all()
    serializer_class = SyncLogSerializer
    
    
class syncPOView(APIView):
    def get_permissions(self):
        return [IsAuthenticated() , HasAppPermission('sap_sync.sync_po')]
    def get(self, request):
        result = POService().syncPOs()
        return Response({"records_synced": result})
    

class syncSinglePOView(APIView):
    def get_permissions(self):
        return [IsAuthenticated() , HasAppPermission('sap_sync.sync_po')]

    def get(self, request, grpo_no):
        result = POService().syncPO(grpo_no)
        return Response({"po_details": result})
    

class DomesticContactListView(generics.ListAPIView):
    def get_permissions(self):
        return [IsAuthenticated() , HasAppPermission('sap_sync.view_domesticcontracts')]

    queryset = DomesticContracts.objects.all()
    serializer_class = DomesticContractSerializer
    
class DomesticContractRetrieveUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    def get_permissions(self):
        if self.request.method == "DELETE":
            return [IsAuthenticated() , HasAppPermission('sap_sync.delete_domesticcontracts')]
        if self.request.method in ['PUT' , 'PATCH']:
            return [IsAuthenticated() , HasAppPermission('sap_sync.change_domesticcontracts')]
            
        return [IsAuthenticated() , HasAppPermission('sap_sync.view_domesticcontracts')]
        
    queryset = DomesticContracts.objects.all()
    serializer_class = DomesticContractSerializer
    lookup_field = 'id'



class syncBalanceSheet(APIView):
    def get_permissions(self):
        return [IsAuthenticated() , HasAppPermission('sap_sync.sync_balance_sheet')]

    def get(self, request):
        result = BalanceSheetService().syncBalanceSheet()
        return Response({"balance_sheet": result})
    
class syncBalanceSheetInsights(APIView):
    def get_permissions(self):
        return [IsAuthenticated() , HasAppPermission('sap_sync.sync_balance_sheet')]

    def get(self, request):
        result = BalanceSheetService().syncInsights()
        return Response({"balance_sheet_insights": result})
    
class syncOpenGRPOS(APIView):
    def get_permissions(self):
        return [IsAuthenticated() , HasAppPermission('sap_sync.sync_open_grpos')]

    def get(self, request):
        result = GRPOServices().syncGRPOS()
        return Response({"open_grpos": result})
    

class syncInventory(APIView):
    def get_permissions(self):
        return [IsAuthenticated() , HasAppPermission('sap_sync.sync_inventory')]

    def get(self, request):
        result = InventoryService().syncWarehouseWiseInventory()
        
        return Response({"inventory": result})
    
class syncUniqueWarehouse(APIView):
    def get_permissions(self):
        return [IsAuthenticated() , HasAppPermission('sap_sync.sync_inventory')]
    
    def get(self , request):
        result = InventoryService().getUniqueWarehouse()
        return Response({"unique_warehouse": result})        

class syncFinishedInventory(APIView):
    def get_permissions(self):
        return [IsAuthenticated() , HasAppPermission('sap_sync.sync_inventory')]
    
    def get(self , request):
        result = InventoryService().syncFinishedInventory()
        return Response({"finished_inventory": result})

class DirectorDashboard(APIView):
    def get_permissions(self):
        return [IsAuthenticated()]
    
    def get(self, request):
        
        finished_raw = InventoryService().synfinishedTotal()
        finished_qty_liter = finished_raw[0].get("Finished Qty", 0) if finished_raw else 0
        finished_qty_mts = round(Decimal(str(finished_qty_liter)) / Decimal('1098.9'))

        ec = InventoryService().syncWarehouseTotal('BH-EC')
        ec_ltr = ec[0].get('Liter')
        ec_mts = round(Decimal(str(ec_ltr)) / Decimal('1098.9'))

        fg = InventoryService().syncWarehouseTotal('GP-FG')
        fg_ltr = fg[0].get('Liter')
        fg_mts = round(Decimal(str(fg_ltr)) / Decimal('1098.9'))



        in_tank_liter = TankData.objects.aggregate(
            total_liter=Sum("current_capacity", filter=Q(is_active=True)) 
        )
        in_tank_mts = round((Decimal(in_tank_liter['total_liter']) / Decimal('1.0989'))/1000)

        
        statuses = [
            "ON_THE_WAY", "UNDER_LOADING", "AT_REFINERY", 
            "MUNDRA_PORT", "ON_THE_SEA", "IN_CONTRACT" , "OUT_SIDE_FACTORY"
        ]
        
        aggregations = {}
        for status in statuses:
            prefix = status.lower()
            
            aggregations[f"{prefix}_liter"] = Coalesce(
                Round(Sum("quantity_in_litre", filter=Q(status = status)), precision=0),
                Decimal('0') 
            )
            
            aggregations[f"{prefix}_mts"] = Coalesce(
                Round(Sum("quantity", filter=Q(status = status)) / Decimal('1000'), precision=0),
                Decimal('0')
            )

        # Added .filter(delete=False) right here
        totals = StockStatus.objects.filter(deleted=False).aggregate(**aggregations)
        
        total_at_factory_lts = Decimal(totals['out_side_factory_liter']) +  Decimal(in_tank_liter['total_liter'])
        total_at_factory_mts = Decimal(totals['out_side_factory_mts'] ) +   Decimal(in_tank_mts)
        
        
        return Response({
            "finished": {
                "total" : {"liter" : finished_qty_liter , "mts" : finished_qty_mts},
                "BH-EC" : {"liter" : ec_ltr , "mts" : ec_mts},
                "GP-FG" : {"liter" : fg_ltr , "mts" : fg_mts},
            },
            "at_factory" : {

                "total" : {"total_lts" : total_at_factory_lts , "total_mts" : total_at_factory_mts},
                "in_tank" : {"liter" : in_tank_liter , "mts" : in_tank_mts },
                "outside_factory" : {"liter": totals["out_side_factory_liter"] , "mts" : totals["out_side_factory_mts"]}
            },    
                
            "otw": {"liter": totals["on_the_way_liter"], "mts": totals["on_the_way_mts"]},
            "under_loading": {"liter": totals["under_loading_liter"], "mts": totals["under_loading_mts"]},
            "at_refinery": {"liter": totals["at_refinery_liter"], "mts": totals["at_refinery_mts"]},
            "mundra_port": {"liter": totals["mundra_port_liter"], "mts": totals["mundra_port_mts"]},
            "on_the_sea": {"liter": totals["on_the_sea_liter"], "mts": totals["on_the_sea_mts"]},
            "in_contract": {"liter": totals["in_contract_liter"], "mts": totals["in_contract_mts"]}
        })
        
        
class getOpenAP(APIView):
    def get(self , request):
        result = APService().getAllOpenAP()
        return Response({"Open APs" : result})