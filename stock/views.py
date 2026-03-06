from rest_framework import generics
from rest_framework.views import APIView
from django_filters import rest_framework as filters
from rest_framework.response import Response
from django.db.models import Sum, F, Subquery, OuterRef, DateTimeField
from decimal import Decimal
from collections import defaultdict, OrderedDict


from .models import StockStatus ,StockStatusUpdateLog
from .serializers import StockStatusSerializer , StockStatusUpdateLogSerializer
from accounts.permissions import IsAdminUser , IsFactoryUser , IsManagerUser
from .filters import StockStatusFilters
from tank.models import TankData


class StockStatusListCreateView(generics.ListCreateAPIView):
    queryset = StockStatus.objects.filter(deleted=False)
    serializer_class = StockStatusSerializer
    permission_classes = [IsAdminUser]
    filter_backends = (filters.DjangoFilterBackend,) 
    filterset_class = StockStatusFilters


class StockStatusUpdateRetrieveDeleteView(generics.RetrieveUpdateDestroyAPIView):
    queryset = StockStatus.objects.all()
    serializer_class = StockStatusSerializer
    permission_classes = [IsAdminUser]
    lookup_field =  'id'

class StockUpdateLogListView(generics.ListAPIView):
    queryset = StockStatusUpdateLog.objects.all()
    serializer_class = StockStatusUpdateLogSerializer
    permission_classes = [IsAdminUser]


class StockStatusInsights(APIView):
    
    def get(self, request):
        queryset = StockStatus.objects.filter(deleted=False)
        filterset = StockStatusFilters(request.GET, queryset=queryset)
        if filterset.is_valid():
            queryset = filterset.qs
        # FIXED: Use Count('id') for the total number of records
        insights = queryset.aggregate(
            total_value=Sum("total"),
            total_qty=Sum('quantity'),
            total_count=Count('id')
        )

        total_value = insights['total_value'] or Decimal('0.00')
        total_qty = insights['total_qty'] or Decimal('0.00')

        if total_qty > 0:
            avg_price_per_kg = round(total_value / total_qty, 2)
            # 1 litre of oil = 0.92 kg, so price_per_ltr = price_per_kg * 0.92
            avg_price_per_ltr = round(avg_price_per_kg * Decimal('0.92'), 2)
        else:
            avg_price_per_kg = Decimal('0.00')
            avg_price_per_ltr = Decimal('0.00')

        insights['avg_price_per_kg'] = avg_price_per_kg
        insights['avg_price_per_ltr'] = avg_price_per_ltr

        return Response({
            "summary": insights,
        })


class StockStatusSummary(APIView):

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
            avg_price_per_ltr = round(avg_price_per_kg * Decimal('0.92'), 2)
        else:
            avg_price_per_kg = Decimal('0.00')
            avg_price_per_ltr = Decimal('0.00')

        summary['avg_price_per_kg'] = avg_price_per_kg
        summary['avg_price_per_ltr'] = avg_price_per_ltr

        return Response({
            "summary": summary,
        })






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



def allocate_fifo(tank_qty, completed_entries):
    """
    FIFO allocation: the stock REMAINING in the tank is the NEWEST stock.

    Walk through completed entries from newest → oldest, allocating
    quantity until the tank total is fully accounted for.

    Args:
        tank_qty: float — total current_capacity from tank meters
        completed_entries: list of dicts with 'rate', 'quantity', 'vendor',
                          already ordered newest-first

    Returns:
        list of dicts: [{'rate': float, 'qty': float, 'vendor': str}, ...]
    """
    remaining = float(tank_qty)
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

    # If tank has more than sum of COMPLETED entries (measurement variance),
    # add the remainder as "unallocated"
    if remaining > 0:
        allocations.append({
            'rate': 0,
            'qty': remaining,
            'vendor': 'Unallocated',
        })

    return allocations


class StockDashboard(APIView):

    def get(self, request):

        # ────────────────────────────────────────────────────────────
        # 1.  IN FACTORY — Tank totals per item
        # ────────────────────────────────────────────────────────────
        tank_qs = (
            TankData.objects
            .filter(is_active=True, item_code__isnull=False)
            .values(item=F('item_code__tank_item_code'))
            .annotate(qty=Sum('current_capacity'))
        )
        in_factory_map = {
            row['item']: float(row['qty'] or 0) for row in tank_qs
        }

        # ────────────────────────────────────────────────────────────
        # 1b. IN FACTORY — FIFO rate breakdown from COMPLETED entries
        #
        #     Use StockStatusUpdateLog to find the ACTUAL timestamp
        #     when each entry became COMPLETED, then sort newest first.
        # ────────────────────────────────────────────────────────────

        # Subquery: get the timestamp when this stock entry became COMPLETED
        completed_at_subquery = (
            StockStatusUpdateLog.objects
            .filter(
                stock_id=OuterRef('pk'),
                field_name='status',
                new_value='COMPLETED',
            )
            .order_by('-updated_at')    # latest log wins (in case of multiple)
            .values('updated_at')[:1]
        )

        completed_qs = (
            StockStatus.objects
            .filter(deleted=False, status='COMPLETED')
            .annotate(
                completed_at=Subquery(completed_at_subquery, output_field=DateTimeField())
            )
            # Primary sort: actual completed timestamp from log (newest first)
            # Fallback: created_at if no log entry exists
            .order_by(F('completed_at').desc(nulls_last=True), '-created_at')
            .values(
                'item_code_id',
                'rate',
                'quantity',
                'completed_at',
                vendor=F('vendor_code__card_name'),
            )
        )

        # Group completed entries by item_code, preserving order (newest first)
        completed_by_item = defaultdict(list)
        for row in completed_qs:
            completed_by_item[row['item_code_id']].append(row)

        # Run FIFO allocation for each item that has tank stock
        in_factory_rates = {}
        for item_code, tank_qty in in_factory_map.items():
            if tank_qty > 0:
                entries = completed_by_item.get(item_code, [])
                in_factory_rates[item_code] = allocate_fifo(tank_qty, entries)
            else:
                in_factory_rates[item_code] = []

        # ────────────────────────────────────────────────────────────
        # 2.  OUTSIDE FACTORY  (no vendor breakdown)
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
        #     Excludes OUT_SIDE_FACTORY and COMPLETED (already in factory)
        # ────────────────────────────────────────────────────────────
        stock_qs = (
            StockStatus.objects
            .filter(deleted=False)
            .exclude(status__in=['OUT_SIDE_FACTORY', 'COMPLETED'])
            .values('item_code_id', 'status', vendor_name=F('vendor_code__card_name'))
            .annotate(qty=Sum('quantity'))
        )

        status_vendors = defaultdict(set)
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

        # Merge item codes from all sources
        all_items.update(in_factory_map.keys())
        all_items.update(outside_factory_map.keys())

        # ────────────────────────────────────────────────────────────
        # 4.  BUILD ORDERED STATUS → VENDORS MAP
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

        for item_code in sorted(all_items):
            in_fac  = in_factory_map.get(item_code, 0)
            out_fac = outside_factory_map.get(item_code, 0)
            row_total = in_fac + out_fac

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
                'in_factory_rates': in_factory_rates.get(item_code, []),
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
        