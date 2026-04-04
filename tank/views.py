from django.shortcuts import render
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from collections import defaultdict
from django.db.models import Sum, F, Subquery, OuterRef, DateTimeField, Count , Q


from decimal import Decimal
from rest_framework import status, serializers
from .models import TankLayer, TankLog, TankLogConsumption
from .services import TankService , ItemAvergaCost
from stock.models import StockStatus, StockStatusUpdateLog
from .models import TankItem, TankData 
from .serializers import TankItemSerializer, TankDataSerializer , TankItemColorSerialier ,TankDataCapacitySerializer , TankInwardSerializer , TankOutwardSerializer , TankTransferSerializer , TankLayerResponseSerializer , TankLogResponseSerializer ,TankConsumptionSerializer, TankLogConsumptionResponseSerializer , TransferTankSerialier , TankLogSerializer
from accounts.permissions import IsAdminUser , IsManagerUser , IsFactoryUser


    
# TANK DATA VIEWS
  
class TankDataView(generics.RetrieveDestroyAPIView):
    queryset = TankData.objects.all()
    serializer_class = TankDataSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'tank_code'
    
    def get_permissions(self):
        if self.request.method == 'GET':
            return [IsAuthenticated()]
        
        return [IsAdminUser()]


class TankDataListCrateView(generics.ListCreateAPIView):
    queryset = TankData.objects.all()
    serializer_class = TankDataSerializer
    
    def get_permissions(self):
        if self.request.method == 'GET':
            return [IsAuthenticated()]
        
        return [IsAuthenticated(), (IsAdminUser | IsManagerUser)()]

class TankCapacityUpdateView(generics.UpdateAPIView):
    queryset = TankData.objects.all()
    serializer_class = TankDataCapacitySerializer
    lookup_field = 'tank_code'
    permission_classes = [IsAuthenticated, IsAdminUser | IsFactoryUser]
    
    

# TANK ITEM VIEWS
class TankItemViews(generics.RetrieveDestroyAPIView):
    queryset = TankItem.objects.all()
    serializer_class = TankItemSerializer
    lookup_field = 'tank_item_code'
    
    def get_permissions(self):
        if self.request.method == 'GET':
            return [IsAuthenticated()]
        
        return [IsAdminUser()]
    
class TankItemListCreateView(generics.ListCreateAPIView):
    queryset = TankItem.objects.all()
    serializer_class = TankItemSerializer
    
    def get_permissions(self):
        if self.request.method == 'GET':
            return [IsAuthenticated()]

        return [IsAuthenticated(), (IsAdminUser | IsManagerUser)()]  
   
class TankItemColorUpdateView(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated, IsAdminUser | IsManagerUser]
    queryset = TankItem.objects.all()
    serializer_class = TankItemColorSerialier
    lookup_field = 'tank_item_code'


class TankDataSummary(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser | IsManagerUser | IsFactoryUser]

    def get(self, request):
        queryset = TankData.objects.filter(is_active=True)

        data = queryset.aggregate(
            total_tank_capacity=Sum('tank_capacity'),
            current_stock=Sum('current_capacity'),
            tank_count=Count('tank_code'),
            item_count=Count('item_code', distinct=True)
        )

        total_tank_capacity = data['total_tank_capacity'] or Decimal('0.00')
        current_stock = data['current_stock'] or Decimal('0.00')

        if total_tank_capacity > 0:
            utilisation_rate = round((current_stock / total_tank_capacity) * 100, 2)
        else:
            utilisation_rate = Decimal('0.00')

        return Response({
            "summary": {
                "total_tank_capacity": total_tank_capacity,
                "current_stock": current_stock,
                "utilisation_rate": utilisation_rate,
                "tank_count": data['tank_count'],
                "item_count": data['item_count'],
            }
        })


class TankItemWiseSummary(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser | IsManagerUser | IsFactoryUser]

    def get(self, request):
        queryset = TankData.objects.filter(is_active=True, item_code__isnull=False)

        item_data = queryset.values(
            'item_code__tank_item_code',
            'item_code__tank_item_name',
            'item_code__color'
        ).annotate(
            quantity_in_liters=Sum('current_capacity'),
            total_capacity=Sum('tank_capacity'),
            tank_count=Count('tank_code')
        )

        results = []
        grand_total_quantity = Decimal('0.00')
        for item in item_data:
            tank_codes = list(
                queryset.filter(item_code=item['item_code__tank_item_code'])
                .values_list('tank_code', flat=True)
            )
            qty = item['quantity_in_liters'] or Decimal('0.00')
            grand_total_quantity += qty
            results.append({
                "color": item['item_code__color'],
                "tank_item_code": item['item_code__tank_item_code'],
                "tank_item_name": item['item_code__tank_item_name'],
                "quantity_in_liters": qty,
                "total_capacity": item['total_capacity'] or Decimal('0.00'),
                "tank_count": item['tank_count'],
                "tank_numbers": tank_codes,
            })

        return Response({
            "total_quantity": grand_total_quantity,
            "items": results,
        })
    



class TankCapacityInsights(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser | IsManagerUser | IsFactoryUser]

    def get(self, request):
        aggregate = TankData.objects.aggregate(
            total_capacity=Sum('tank_capacity'),
            current_capacity=Sum('current_capacity')
        )
        
        total_capacity = aggregate['total_capacity'] or 0
        filled_capacity = aggregate['current_capacity'] or 0
        
        if total_capacity == 0:
            return Response({
                "total_capacity": 0,
                "filled_capacity": 0,
                "filled_percentage": 0,
                "empty_capacity": 0,
                "empty_percentage": 0
            })
        
        empty_capacity = total_capacity - filled_capacity
        filled_percentage = round((filled_capacity / total_capacity) * 100, 2)
        empty_percentage = round((empty_capacity / total_capacity) * 100, 2)

        return Response({
            "total_capacity": total_capacity,
            "filled_capacity": filled_capacity,
            "filled_percentage": filled_percentage,
            "empty_capacity": empty_capacity,
            "empty_percentage": empty_percentage
        })

def allocate_fifo(total_qty, completed_entries):
    """
    FIFO: remaining stock = newest deliveries.
    Walk newest → oldest, allocating until total_qty is filled.

    Args:
        total_qty: float — total current_capacity for this item across all tanks
        completed_entries: list of dicts, ordered newest-first, with
                          'rate', 'quantity', 'vendor'

    Returns:
        list of dicts: [{'rate': float, 'qty': float, 'vendor': str}, ...]
    """
    remaining = float(total_qty)
    allocations = []

    for entry in completed_entries:
        if remaining <= 0:
            break

        entry_qty = float(entry['quantity'] or 0)
        entry_rate = float(entry['rate'] or 0)

        allocated = min(remaining, entry_qty)
        allocations.append({
            'rate': entry_rate,
            'qty': allocated,
            'vendor': entry.get('vendor', ''),
        })
        remaining -= allocated

    if remaining > 0:
        allocations.append({
            'rate': 0,
            'qty': remaining,
            'vendor': 'Unallocated',
        })

    return allocations


def distribute_to_tank(tank_qty, item_total, item_allocations):
    """
    Proportionally distribute item-level FIFO allocations to a single tank.

    Args:
        tank_qty: float — this tank's current_capacity
        item_total: float — total current_capacity for this item across ALL tanks
        item_allocations: list from allocate_fifo()

    Returns:
        list of dicts with proportional quantities, and weighted avg rate
    """
    if item_total <= 0 or tank_qty <= 0:
        return [], 0

    ratio = tank_qty / item_total
    breakdown = []
    total_value = 0

    for alloc in item_allocations:
        proportional_qty = round(alloc['qty'] * ratio, 2)
        if proportional_qty > 0:
            percentage = round((proportional_qty / tank_qty) * 100, 2)
            breakdown.append({
                'rate': alloc['rate'],
                'qty': proportional_qty,
                'percentage': percentage,
                'vendor': alloc['vendor'],
            })
            total_value += proportional_qty * alloc['rate']

    weighted_avg = round(total_value / tank_qty, 2) if tank_qty > 0 else 0

    return breakdown, weighted_avg


class TankRateBreakdownView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):

        tanks = (
            TankData.objects
            .filter(is_active=True, item_code__isnull=False)
            .select_related('item_code')
            .order_by('item_code__tank_item_code', 'tank_code')
        )

        # ────────────────────────────────────────────────────────────
        # 2. Sum current_capacity per item (across all tanks)
        # ────────────────────────────────────────────────────────────
        item_totals_qs = (
            TankData.objects
            .filter(is_active=True, item_code__isnull=False)
            .values(item=F('item_code__tank_item_code'))
            .annotate(total=Sum('current_capacity'))
        )
        item_totals = {
            row['item']: float(row['total'] or 0) for row in item_totals_qs
        }

        # ────────────────────────────────────────────────────────────
        # 3. FIFO: get COMPLETED entries per item, ordered by actual
        #    completion date from update log (newest first)
        # ────────────────────────────────────────────────────────────
        completed_at_subquery = (
            StockStatusUpdateLog.objects
            .filter(
                stock_id=OuterRef('pk'),
                field_name='status',
                new_value='COMPLETED',
            )
            .order_by('-updated_at')
            .values('updated_at')[:1]
        )

        completed_qs = (
            StockStatus.objects
            .filter(deleted=False, status='COMPLETED')
            .annotate(
                completed_at=Subquery(
                    completed_at_subquery,
                    output_field=DateTimeField()
                )
            )
            .order_by(F('completed_at').desc(nulls_last=True), '-created_at')
            .values(
                'item_code_id',
                'rate',
                'quantity',
                vendor=F('vendor_code__card_name'),
            )
        )

        completed_by_item = defaultdict(list)
        for row in completed_qs:
            completed_by_item[row['item_code_id']].append(row)

        fifo_by_item = {}
        for item_code, total in item_totals.items():
            if total > 0:
                entries = completed_by_item.get(item_code, [])
                fifo_by_item[item_code] = allocate_fifo(total, entries)
            else:
                fifo_by_item[item_code] = []

        results = []
        for tank in tanks:
            item_code = tank.item_code.tank_item_code
            tank_qty = float(tank.current_capacity or 0)
            item_total = item_totals.get(item_code, 0)
            item_allocs = fifo_by_item.get(item_code, [])

            breakdown, weighted_avg = distribute_to_tank(
                tank_qty, item_total, item_allocs
            )

            results.append({
                'tank_code': tank.tank_code,
                'item_code': item_code,
                'item_name': tank.item_code.tank_item_name,
                'color': tank.item_code.color,
                'tank_capacity': float(tank.tank_capacity or 0),
                'current_capacity': tank_qty,
                'rate_breakdown': breakdown,
                'weighted_avg_rate': weighted_avg,
            })

        return Response(results)





 
class TankInwardView(APIView):
    """
    POST /tank/inward/
    Body: { "tank_code": "TNK001", "stock_status_id": 45, "quantity": 30.00 }
    """
    permission_classes = [IsAuthenticated, IsAdminUser | IsFactoryUser]
 
    def post(self, request):
        serializer = TankInwardSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
 
        try:
            result = TankService.inward(
                tank_code=serializer.validated_data['tank_code'],
                stock_status_id=serializer.validated_data['stock_status_id'],
                quantity=serializer.validated_data['quantity'],
                created_by=request.user,
            )
 
            return Response({
                'message': 'Inward entry successful',
                'layer': TankLayerResponseSerializer(result['layer']).data,
                'log': TankLogResponseSerializer(result['log']).data,
                'stock_split': result['stock_split'],
                'remainder_quantity': result['remainder_quantity'],
            }, status=status.HTTP_201_CREATED)
 
        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {'error': f'Unexpected error: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
 
 
class TankOutwardView(APIView):
    """
    POST /tank/outward/
    Body: { "tank_code": "TNK001", "quantity": 50.00, "remarks": "Production batch #123" }
    """
    permission_classes = [IsAuthenticated, IsAdminUser | IsFactoryUser]
 
    def post(self, request):
        serializer = TankOutwardSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
 
        try:
            result = TankService.outward(
                tank_code=serializer.validated_data['tank_code'],
                quantity=serializer.validated_data['quantity'],
                created_by=request.user,
                remarks=serializer.validated_data.get('remarks', ''),
            )
 
            return Response({
                'message': 'Outward entry successful',
                'log': TankLogResponseSerializer(result['log']).data,
                'cost_breakdown': result['cost_breakdown'],
            }, status=status.HTTP_201_CREATED)
 
        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {'error': f'Unexpected error: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
 
 
class TankTransferView(APIView):
    """
    POST /tank/transfer/
    Body: { "source_tank_code": "TNK001", "destination_tank_code": "TNK002", "quantity": 50.00, "remarks": "" }
    """
    permission_classes = [IsAuthenticated, IsAdminUser | IsFactoryUser]

    def post(self, request):
        serializer = TankTransferSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            result = TankService.transfer(
                source_tank_code=serializer.validated_data['source_tank_code'],
                destination_tank_code=serializer.validated_data['destination_tank_code'],
                quantity=serializer.validated_data['quantity'],
                created_by=request.user,
                remarks=serializer.validated_data.get('remarks', ''),
            )

            return Response({
                'message': 'Transfer successful',
                'log': TankLogResponseSerializer(result['log']).data,
                'source_tank': result['source_tank'],
                'destination_tank': result['destination_tank'],
                'quantity_transferred': result['quantity_transferred'],
            }, status=status.HTTP_201_CREATED)

        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {'error': f'Unexpected error: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class TankStatusView(APIView):
    """
    GET /tank/<tank_code>/layers/
    Returns active layers with cost breakdown for a specific tank.
    """
    permission_classes = [IsAuthenticated]
 
    def get(self, request, tank_code):
        try:
            tank = TankData.objects.get(tank_code=tank_code)
        except TankData.DoesNotExist:
            return Response(
                {'error': f'Tank {tank_code} not found'},
                status=status.HTTP_404_NOT_FOUND
            )
 
        tank_status = TankService.get_tank_status(tank_code)
 
        return Response({
            'tank_code': tank.tank_code,
            'tank_capacity': tank.tank_capacity,
            'current_capacity': tank.current_capacity,
            **tank_status,
        })
 
 
class TankLogsView(APIView):
    """
    GET /tank/<tank_code>/logs/
    Returns all inward/outward events for a tank (passbook view).
    """
    permission_classes = [IsAuthenticated]
 
    def get(self, request, tank_code):
        try:
            tank = TankData.objects.get(tank_code=tank_code)
        except TankData.DoesNotExist:
            return Response(
                {'error': f'Tank {tank_code} not found'},
                status=status.HTTP_404_NOT_FOUND
            )
 
        logs = (
            TankLog.objects
            .filter(tank_code=tank)
            .prefetch_related(
                'consumptions__tank_layer__stock_status__vendor_code',
            )
            .select_related('stock_status', 'tank_layer', 'tank_code', 'destination_tank')
            .order_by('-created_at')
        )
 
        serializer = TankLogResponseSerializer(logs, many=True)
 
        return Response({
            'tank_code': tank.tank_code,
            'logs': serializer.data,
        })
 
class TankConsumptionView(generics.ListAPIView):
    
    permission_classes = [IsAuthenticated]
    queryset = TankLogConsumption.objects.all()
    serializer_class = TankConsumptionSerializer
    
class TankLogView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    queryset = TankLog.objects.all()
    serializer_class = TankLogSerializer
    
    
class EmptyorSameTanks(APIView):
    def get(self, request):
        item_code = request.query_params.get('item_code')
        empty_or_same_tanks = TankData.objects.filter(Q(item_code=item_code) | Q(current_capacity=Decimal(0.00)) | Q(current_capacity__isnull=True))
        serializer = TransferTankSerialier(empty_or_same_tanks, many=True)
        return Response(serializer.data)
    

class ItemWiseAverage(APIView):
    def get(self , request):
        item_code = request.query_params.get('item_code')
        response = ItemAvergaCost(item_code)
        return Response(response)
        
class EmptyTank(APIView):
    def patch(self , request):
        tank_code = request.query_params.get('tank_code')
        tank = TankData.objects.get(tank_code=tank_code)
        
        tank.current_capacity = Decimal(0.00)
        tank.item_code = None
        
        tank.save()
        return Response({"Tank Emptied Successfully"})
        