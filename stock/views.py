from rest_framework import generics
from rest_framework.views import APIView
from django_filters import rest_framework as filters
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Sum, Case, When, DecimalField, Value , Count , F
from decimal import Decimal
from collections import defaultdict, OrderedDict


from .models import StockStatus ,StockStatusUpdateLog
from .serializers import StockStatusSerializer , StockStatusUpdateLogSerializer
from .services import arrive_batch , dispatch , move
from accounts.permissions import IsAdminUser , IsFactoryUser , IsManagerUser
from .filters import StockStatusFilters
from tank.models import TankData


class StockStatusListCreateView(generics.ListCreateAPIView):
    queryset = StockStatus.objects.filter(deleted=False)
    serializer_class = StockStatusSerializer
    permission_classes = [IsAdminUser | IsManagerUser]
    filter_backends = (filters.DjangoFilterBackend,) 
    filterset_class = StockStatusFilters


class StockStatusUpdateRetrieveDeleteView(generics.RetrieveUpdateDestroyAPIView):
    queryset = StockStatus.objects.all()
    serializer_class = StockStatusSerializer
    permission_classes = [IsAdminUser | IsManagerUser]
    lookup_field =  'id'

class StockUpdateLogListView(generics.ListAPIView):
    queryset = StockStatusUpdateLog.objects.all()
    serializer_class = StockStatusUpdateLogSerializer
    permission_classes = [IsAdminUser | IsManagerUser]


class StockStatusInsights(APIView):
    
    permission_classes = [IsAuthenticated, IsAdminUser | IsManagerUser]

    def get(self, request):
        queryset = StockStatus.objects.filter(deleted=False)
        filterset = StockStatusFilters(request.GET, queryset=queryset)
        if filterset.is_valid():
            queryset = filterset.qs
            insights = queryset.aggregate(
            total_value=Sum("total"),
            total_qty=Sum('quantity'),
            total_count=Count('id')
        )

        total_value = insights['total_value'] or Decimal('0.00')
        total_qty = insights['total_qty'] or Decimal('0.00')

        if total_qty > 0:
            avg_price_per_kg = round(total_value / total_qty, 2)
            # 1 litre = 1 kg * 1.0989, so price_per_ltr = price_per_kg / 1.0989
            avg_price_per_ltr = round(avg_price_per_kg / Decimal('1.0989'), 2)
        else:
            avg_price_per_kg = Decimal('0.00')
            avg_price_per_ltr = Decimal('0.00')

        insights['avg_price_per_kg'] = avg_price_per_kg
        insights['avg_price_per_ltr'] = avg_price_per_ltr

        return Response({
            "summary": insights,
        })


class StockStatusSummary(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser | IsManagerUser]
    def get(self, request):
        queryset = StockStatus.objects.filter(deleted=False)

        summary = queryset.aggregate(
            total_value=Sum("total"),
            total_qty=Sum('quantity'),
            total_count=Count('id')
        )

        total_value = summary['total_value'] or Decimal('0.00')
        total_qty = summary['total_qty'] or Decimal('0.00')

        if total_qty > 0:
            avg_price_per_kg = round(total_value / total_qty, 2)
            avg_price_per_ltr = round(avg_price_per_kg / Decimal('1.0989'), 2)
        else:
            avg_price_per_kg = Decimal('0.00')
            avg_price_per_ltr = Decimal('0.00')

        summary['avg_price_per_kg'] = avg_price_per_kg
        summary['avg_price_per_ltr'] = avg_price_per_ltr

        return Response({
            "summary": summary,
        })

class OutsideFactoryStock(APIView):
    permission_classes = [IsAdminUser | IsManagerUser]
    def get(self,request):
        queryset = StockStatus.objects.filter(deleted=False, status='OUT_SIDE_FACTORY')
        serializer = StockStatusSerializer(queryset, many=True)
        return Response(serializer.data)
    
    
class GetUniqueRM(APIView):
    permission_classes = [IsAdminUser | IsManagerUser]
    def get(self, request):
        codes = (
            StockStatus.objects
            .filter(deleted=False , status = 'COMPLETED')
            .values_list('item_code', flat=True)
            .distinct()
        )
        return Response(list(codes))

class GetStockEntrybyRM(APIView):
    permission_classes = [IsAdminUser | IsManagerUser]
    def get(self, request):
        item_code = request.query_params.get('item_code')

        if not item_code:
            return Response({"error": "item_code is required"}, status=400)

        queryset = (
            StockStatus.objects
            .filter(deleted=False, item_code=item_code, status='COMPLETED')
            .values('id', 'vendor_code', 'vendor_code__card_name', 'rate', 'quantity', 'quantity_in_litre','total', 'vehicle_number', 'transporter', 'location', 'eta', 'created_at')
            .order_by('-created_at')
        )

        return Response(list(queryset))



STATUS_DISPLAY_ORDER = [
    'ON_THE_WAY',
    'UNDER_LOADING',
    'AT_REFINERY',
    'OTW_TO_REFINERY',
    'KANDLA_STORAGE',
    'MUNDRA_PORT',
    'ON_THE_SEA',
    'IN_CONTRACT',
    'IN_TRANSIT',
    'PENDING',
    'PROCESSING',
    'COMPLETED',
    'DELIVERED',
    
]

ITEM_CODE_DISPLAY_ORDER = [
    'RM0CDRO',
    'RM00C01',
    'RM00CPC',
    'RM00C02',
    'RM00SBR',
    'RMMKG01',
    'RM0GNCP',
    'RM00GNR',
    'RM00GNR02',
    'RM00RBR',
    'RM00RBD',
    'RM00CSR',
    'RM0SESM',
    'RM00P01',
    'RM0EL01',
    'RM0EV01'
]

class StockDashboard(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser | IsManagerUser]
    def get(self, request):
        tank_qs = (
            StockStatus.objects
            .filter(deleted=False, status='IN_TANK')
            .values('item_code_id')
            .annotate(qty=Sum('quantity'))
        )
        in_factory_map = {
            row['item_code_id']: float(row['qty'] or 0)  for row in tank_qs
        }

        # ────────────────────────────────────────────────────────────
        outside_qs = (
            StockStatus.objects
            .filter(deleted=False, status='OUT_SIDE_FACTORY')
            .values('item_code_id')
            .annotate(qty=Sum('quantity'))
        )
        outside_factory_map = {
            row['item_code_id']: float(row['qty'] or 0) for row in outside_qs
        }

        # ────────────────────────────────────────────────────────────
        # 3.  ALL OTHER STATUSES  (with vendor sub-columns)
        # ────────────────────────────────────────────────────────────
        stock_qs = (
            StockStatus.objects
            .filter(deleted=False)
            .exclude(status='OUT_SIDE_FACTORY')
            .values('item_code_id', 'status', vendor_name=F('vendor_code__card_name'))
            .annotate(qty=Sum('quantity'))
        )

        # status_vendors : {status: {vendor_name, ...}}
        status_vendors = defaultdict(set)
        # item_data : {item_code: {(status, vendor): qty}}
        item_data = defaultdict(lambda: defaultdict(float))
        all_items = set()

        for row in stock_qs:
            item   = row['item_code_id']
            status = row['status']
            vendor = row['vendor_name']
            qty    = float(row['qty'] or 0)

            status_vendors[status].add(vendor)
            item_data[item][(status, vendor)] = qty
            all_items.add(item)

        # Merge item codes from all three sources
        all_items.update(in_factory_map.keys())
        all_items.update(outside_factory_map.keys())

        # ────────────────────────────────────────────────────────────
        # 4.  BUILD ORDERED STATUS → VENDORS MAP
        #     (only statuses that have data, in display order)
        # ────────────────────────────────────────────────────────────
        ordered_status_vendors = OrderedDict()
        for status in STATUS_DISPLAY_ORDER:
            if status in status_vendors and status_vendors[status]:
                ordered_status_vendors[status] = sorted(status_vendors[status])
                



        # ────────────────────────────────────────────────────────────
        # 5.  ASSEMBLE ITEM ROWS + COLUMN TOTALS
        # ────────────────────────────────────────────────────────────
        items = []
        total_in_factory = 0
        total_outside_factory = 0
        status_vendor_totals = defaultdict(float)
        
        ordered_items = [ic for ic in ITEM_CODE_DISPLAY_ORDER if ic in all_items]
        ordered_items += sorted(all_items - set(ITEM_CODE_DISPLAY_ORDER))
        
        for item_code in ordered_items:
            in_fac  = in_factory_map.get(item_code, 0)
            out_fac = outside_factory_map.get(item_code, 0)
            row_total = in_fac + out_fac

            # Build status__vendor cells
            status_data = {}
            for status, vendors in ordered_status_vendors.items():
                for vendor in vendors:
                    key = f"{status}__{vendor}"
                    val = item_data[item_code].get((status, vendor), 0)
                    status_data[key] = val
                    row_total += val
                    status_vendor_totals[key] += val

            items.append({
                'item_code': item_code,
                'in_factory': in_fac,
                'outside_factory': out_fac,
                'status_data': status_data,
                'total': row_total,
            })

            total_in_factory += in_fac
            total_outside_factory += out_fac

        grand_total = sum(item['total'] for item in items)
        active_items = sum(1 for item in items if item['total'] > 0)

        # ────────────────────────────────────────────────────────────
        # 6.  RESPONSE
        # ────────────────────────────────────────────────────────────
        return Response({
            'summary': {
                'in_factory_total': total_in_factory,
                'outside_factory_total': total_outside_factory,
                'active_items': active_items,
            },
            'status_vendors': ordered_status_vendors,
            'items': items,
            'totals': {
                'in_factory': total_in_factory,
                'outside_factory': total_outside_factory,
                'status_vendor_totals': dict(status_vendor_totals),
                'grand_total': grand_total,
            },
        })



class Dispatch(APIView):
    def post(self,request):
        dispatch_status = request.data.get('destination_status')
        source_id = request.data.get('stock_id')
        dispatch_quantity = request.data.get('quantity')
        action = request.data.get('action')
        created_by = request.data.get('created_by')
        
        stock = StockStatus.objects.get(id=source_id)
        new_record = dispatch(stock, dispatch_quantity, dispatch_status , created_by , action)
        
        serializer = StockStatusSerializer(new_record)
        return Response(serializer.data)
    
class ArriveBatch(APIView):
    def post(self,request):
        otw_id = request.data.get('stock_id')
        action = request.data.get('action')
        destination_status = request.data.get('destination_status')
        weighed_qty = request.data.get('weighed_qty')
        created_by = request.data.get('created_by')
        
        otw_record = StockStatus.objects.get(id=otw_id)
        
        accumulator = arrive_batch(otw_record, weighed_qty, created_by ,action, destination_status) 
        
        serializer = StockStatusSerializer(accumulator)
        return Response(serializer.data)
    
class MoveView(APIView):
    def post(self,request):
        stock_id =  request.data.get('stock_id')
        new_quantity = request.data.get('new_quantity')
        action = request.data.get('action')
        created_by = request.data.get('created_by')
        new_status = request.data.get('new_status')
        
        stock = StockStatus.objects.get(id=stock_id)
        new_record = move(stock, new_quantity, action, new_status,created_by)
        
        serializer = StockStatusSerializer(new_record)
        return Response(serializer.data)
    
class InTankLogView(APIView):
    def get(delf,request):
        queryset = StockStatusUpdateLog.objects.filter()
    