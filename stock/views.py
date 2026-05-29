from rest_framework import generics , status
from rest_framework.views import APIView
from django_filters import rest_framework as filters
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Sum, Case, When, DecimalField, Value , Count , F , ExpressionWrapper , FloatField , Count , Max
from decimal import Decimal
from collections import defaultdict, OrderedDict
from django.db.models.functions import Round


from .models import StockStatus ,StockStatusUpdateLog , StockStatusFieldLog ,StockStatusChangeSession , DebitEntry , ContractualHistory , DashboardSnapshot
from .serializers import StockStatusSerializer , StockStatusUpdateLogSerializer , StockStatusPatchSerializer , StockStatusChangeSessionSerializer , StockStatusFieldLogSerializer , DebitEntrySerializer , ContractualHistorySerializer , DashboardSnapshotSerialixer
from .services import arrive_batch , dispatch , move , create_audit, TRACKED_FIELDS
from .filters import StockStatusFilters
from tank.models import TankData ,TankItem
from sap_sync.models import Party
from accounts.permissions import HasAppPermission

class StockStatusListCreateView(generics.ListCreateAPIView):
    def  get_permissions(self):
        if self.request.method == "POST":
            return [IsAuthenticated() , HasAppPermission('stock.add_stockstatus')]
        
        return [IsAuthenticated() , HasAppPermission('stock.view_stockstatus')]
        
    def perform_create(self, serializer):
        changed_by = self.request.user.email
        stock = serializer.save(created_by=changed_by)
        create_audit(stock, changed_by_label=changed_by, action='CREATE')

    queryset = StockStatus.objects.filter(deleted=False).exclude(status='COMPLETED')
    serializer_class = StockStatusSerializer
    filter_backends = (filters.DjangoFilterBackend,) 
    filterset_class = StockStatusFilters


class StockStatusUpdateRetrieveDeleteView(generics.RetrieveUpdateDestroyAPIView):
    def get_permissions(self):
        if self.request.method == 'DELETE':
            return [IsAuthenticated() , HasAppPermission('stock.delete_stockstatus')]
        if self.request.method in ['PUT' , 'PATCH']:
            return [IsAuthenticated() , HasAppPermission('stock.change_stockstatus')]
        return [IsAuthenticated() , HasAppPermission('stock.view_stockstatus')]
    
    def perform_update(self, serializer):
        changed_by = self.request.user.email
        old_snapshot = {f: str(getattr(serializer.instance, f)) for f in TRACKED_FIELDS}
        stock = serializer.save(created_by=changed_by)
        create_audit(stock, changed_by_label=changed_by, action='UPDATE', old_snapshot=old_snapshot)

    queryset = StockStatus.objects.all()
    lookup_field = 'id'

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return StockStatusPatchSerializer
        return StockStatusSerializer
    
    def get_serializer(self, *args, **kwargs):
        if self.request.method == 'PATCH':
            kwargs['partial'] = True
        return super().get_serializer(*args, **kwargs)
    
    
class StockUpdateLogListView(generics.ListAPIView):
    def get_permissions(self):
        return [IsAuthenticated() , HasAppPermission('stock.view_stockupdatelog')]
    queryset = StockStatusUpdateLog.objects.all()
    serializer_class = StockStatusUpdateLogSerializer


class StockStatusInsights(APIView):
    
    def get_permissions(self):
        return [IsAuthenticated() , HasAppPermission('stock.view_stockstatus')]
    def get(self, request):

        queryset = StockStatus.objects.filter(deleted=False)
        filterset = StockStatusFilters(request.GET, queryset=queryset)
        if filterset.is_valid():
            queryset = filterset.qs
            insights = queryset.aggregate(
            total_value=Sum(F('quantity') * F('rate')),
            total_qty = Sum('quantity'),
            total_qty_kg=Sum('quantity'),
            total_qty_litre=Sum('quantity_in_litre'),
            total_count=Count('id'),
            weighted_sum_kg=Sum(F('rate') * F('quantity')),
            weighted_sum_liter=Sum(F('quantity_in_litre') * F('rate_in_litres')),
            
        )


        total_value = insights['total_value'] or Decimal('0.00')
        total_qty_kg = insights['total_qty_kg'] or Decimal('0.00')
        total_qty_litre = insights['total_qty_litre'] or Decimal('0.00')
        weighted_sum_litre = insights['weighted_sum_liter'] or Decimal('0.00')
        weighted_sum_kg = insights['weighted_sum_kg'] or Decimal('0.00')

        if total_qty_kg > 0:
            avg_price_per_ltr = round(weighted_sum_litre / total_qty_litre, 2)
            avg_price_per_kg = round(weighted_sum_kg / total_qty_kg, 2)
        else:
            avg_price_per_kg = Decimal('0.00')
            avg_price_per_ltr = Decimal('0.00')

        insights['avg_price_per_kg'] = avg_price_per_kg
        insights['avg_price_per_ltr'] = avg_price_per_ltr

        return Response({
            "summary": insights,
        })


class StockStatusSummary(APIView):
    def get_permissions(self):
        return [IsAuthenticated() , HasAppPermission('stock.view_stockstatus')]

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
    def get_permissions(self):
        return [IsAuthenticated() , HasAppPermission('stock.view_stockstatus')]

    def get(self,request):
        queryset = StockStatus.objects.filter(deleted=False, status='OUT_SIDE_FACTORY')
        serializer = StockStatusSerializer(queryset, many=True)
        return Response(serializer.data)
    
    
class GetUniqueRM(APIView):
    def get_permissions(self):
        return [IsAuthenticated() , HasAppPermission('stock.add_stockstatus')]

    def get(self, request):
        codes = (
            StockStatus.objects
            .filter(deleted=False , status = 'COMPLETED')
            .values_list('item_code', flat=True)
            .distinct()
        )
        return Response(list(codes))

class GetStockEntrybyRM(APIView):
    def get_permissions(self):
        return[IsAuthenticated() , HasAppPermission('stock.view_stockstatus')]

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
    'c2c38f74-2449-483f-b096-4ef91584f782',  # RM0CDRO - CRUDE CANOLA
    '73109f7d-4e6b-46c1-9209-dfcbc463775e',  # RM00C01 - CANOLA
    'a7caf120-054f-4ffe-89ce-2b3c1f5a9718',  # RM00CPC - COLDPRESS CANOLA
    'a4e8fc5d-0e43-45e9-afae-0b6ebdee1dc0',  # RM00C02 - CANOLA 2B

    'e25db225-689b-4fb5-b1c0-d7fcdde5fc70',  # RM00SBR - SOYABEAN
    '4d637889-a625-4f03-8f9d-4babb62fa3be',  # RM00SBD - SOYADEO
    'fca27ec7-a34a-4532-907c-657f89c62501',  # RM0SB02 - SOYABEAN 2B

    'd195cbd9-992b-463a-90f7-484c767bca1f',  # RM00MK01 - MUSTARD KACHI GHANI
    'a8e79643-62ea-4835-9242-5aa5f63aad7b',  # RM0GNCP - GROUNDNUT FILTER

    '4a1d3b03-6540-4373-8220-d072c69c8371',  # RM000SF - SUNFLOWER
    '5c5c043c-d172-49ec-a8cf-bd2a3d409452',  # RM00SF2 - SUNFLOWER OIL 2B
    '77a8fd67-495e-481d-b751-6dcc8323acaa',  # RM00MDO
    'c4a67ea6-b9bd-4051-bdb9-997e2f24b1e5',  # RM000MR - MUSTARD REFINED

    'e6d97064-2345-4ada-ad6e-2da929b62068',  # RMMKG02 - MUSTARD KACHI GHANI 2B

    'b11dc909-4a6b-4f79-9194-1bced0f802a2',  # RM00GNR - GROUNDNUT REFINED
    
    # RM00GNR02 - NOT FOUND IN TABLE
    '5e890081-d306-426e-a5cf-ed989dbf2189',
    '3d6f4ce7-5996-4d60-bdd4-3bb4fb997c2a',  # RM00GD - GOLD

    '3d1056b1-25aa-4663-8c71-4e90790c510b',  # RM00RBR - RICE BRAN REFINED
    '22d62296-c24b-4536-8bcc-821ff379b1d2',  # RM00RBD - RICEDEO
    '516ac941-33e9-4e1c-b1f9-d9e067c9e6f8',  # RM0RB02 - RICEBRAN 2B

    'e9f7e282-8270-488d-a70c-99bc3d8ea701',  # RM00CSR - COTTONSEED
    '5ec9baaa-a208-4916-8a23-376f617ab934',  # RMCSR02 - COTTONSEED 2B

    'a1a93ca9-ffeb-4ea1-a68b-605e28255678',  # RM00VNP - VANASPATI
    '9ea3691d-73b8-4351-8242-d773e4f0e64f',  # RM0CCNT - COCONUT

    'c6420d4c-c736-4f5e-990b-7771b059f1ac',  # RM0SESM - SESAME
    '6bdeafc4-be36-490a-bf9e-c063ae8eb8c6',  # RMSESMT - SESAME TOASTED

    # t2
    '88eeac70-62a0-4158-af25-87a3a96599ca',  # RM00P02 - POMACE 2B
    '12ac4727-f72e-456e-845b-d2597bccf42d',  # RM00P03 - POMACE 3C
    'e601fc1c-2c13-489c-a858-c7132b828293',  # RM0EV02 - EXTRA VIRGIN 2B
    'b9f57f80-9ce6-4a98-a120-b42eecb90896',  # RM0EL02 - EXTRA LIGHT 2B
    'cef9e19e-164a-4026-9ee0-ff090e619925',  # RMSOLIVE - SO OLIVE

    # t3
    'a9da1950-0e88-4fdb-85a3-19f419174a0b',  # RM00P01 - POMACE
    '03cbc3fb-b16f-4fc9-adf2-380787ba06b4',  # RM0EL01 - EXTRA LIGHT
    '8a1de505-adc7-497a-8d89-e654bebadf7a',  # RM0EV01 - EXTRA VIRGIN
    '5949da6f-c2d1-435c-9a7c-13607265e5b8',  # RM0HOSF - HIGH OLIEC SF
]

class StockDashboard(APIView):
    def get_permissions(self):
        return [IsAuthenticated() , HasAppPermission('stock.view_stockstatus')]

    def get(self, request):
        rmcode = request.query_params.get('rmcode')
        status_filter = request.query_params.get('status')
        vendor = request.query_params.get('vendor')

        def apply_common_filters(qs):
            if rmcode:
                qs = qs.filter(item_code__tank_item_code=rmcode)
            if vendor:
                qs = qs.filter(vendor_code__card_code=vendor)
            if status_filter:
                qs = qs.filter(status=status_filter)
            return qs

        # ────────────────────────────────────────────────────────────
        outside_qs = apply_common_filters(
            StockStatus.objects.filter(deleted=False, status='OUT_SIDE_FACTORY')
        ).values('item_code_id').annotate(qty=Sum('quantity'))
        outside_rows = list(outside_qs)

        outside_factory_map = {
            row['item_code_id']: float(row['qty'] or 0) for row in outside_rows
        }

        # ────────────────────────────────────────────────────────────
        # 3.  ALL OTHER STATUSES  (with vendor sub-columns)
        # ────────────────────────────────────────────────────────────
        stock_qs = apply_common_filters(
            StockStatus.objects.filter(deleted=False).exclude(status__in=['OUT_SIDE_FACTORY', 'IN_TANK'])
        ).values(
            'item_code_id',
            'status',
            vendor_name=F('vendor_code__card_name'),
            item_name=Value(''),
        ).annotate(qty=Sum('quantity'))

        # status_vendors : {status: {vendor_name, ...}}
        status_vendors = defaultdict(set)
        # item_data : {item_code: {(status, vendor): qty}}
        item_data = defaultdict(lambda: defaultdict(float))
        all_items = set()
        item_names = {}
        item_sort_ids = {}


        for row in stock_qs:
            item        = row['item_code_id']
            row_status  = row['status']
            row_vendor  = row['vendor_name']
            qty         = float(row['qty'] or 0)

            status_vendors[row_status].add(row_vendor)
            item_data[item][(row_status, row_vendor)] = qty
            item_names[item] = row['item_name']  # ← store name

            all_items.add(item)

        # Merge item codes from both sources
        all_items.update(outside_factory_map.keys())

        item_meta_qs = TankItem.objects.filter(tank_item_code__in=all_items).values(
            'tank_item_code',
            'tank_item_name',
            'id',
        )
        for row in item_meta_qs:
            item_names[row['tank_item_code']] = row['tank_item_name']
            item_sort_ids[row['tank_item_code']] = str(row['id'])

        # ────────────────────────────────────────────────────────────
        # 4.  BUILD ORDERED STATUS → VENDORS MAP
        #     (only statuses that have data, in display order)
        # ────────────────────────────────────────────────────────────
        ordered_status_vendors = OrderedDict()
        for status in STATUS_DISPLAY_ORDER:
            if status in status_vendors and status_vendors[status]:
                ordered_status_vendors[status] = sorted(status_vendors[status], key=lambda vendor: vendor or '')
                



        # ────────────────────────────────────────────────────────────
        # 5.  ASSEMBLE ITEM ROWS + COLUMN TOTALS
        # ────────────────────────────────────────────────────────────
        items = []
        total_outside_factory = 0
        status_vendor_totals = defaultdict(float)
        status_totals = defaultdict(float)


        item_display_order = {
            str(item_uuid): index
            for index, item_uuid in enumerate(dict.fromkeys(ITEM_CODE_DISPLAY_ORDER))
        }

        def item_sort_key(item_code):
            item_uuid = item_sort_ids.get(item_code, str(item_code))
            if item_uuid in item_display_order:
                return (0, item_display_order[item_uuid])
            return (1, str(item_code))

        ordered_items = sorted(all_items, key=item_sort_key)



        for item_code in ordered_items:
            out_fac = outside_factory_map.get(item_code, 0)
            row_total = out_fac

            # Build status__vendor cells
            status_data = {}
            for status, vendors in ordered_status_vendors.items():
                for vendor in vendors:
                    key = f"{status}__{vendor}"
                    val = item_data[item_code].get((status, vendor), 0)
                    status_data[key] = val
                    row_total += val
                    status_vendor_totals[key] += val
                    status_totals[status] += val

            items.append({
                'item_code': item_code,
                'item_name': item_names.get(item_code, ''),  # ← add this
                'outside_factory': out_fac,
                'status_data': status_data,
                'total': row_total,
            })

            total_outside_factory += out_fac

        grand_total = sum(item['total'] for item in items)
        active_items = sum(1 for item in items if item['total'] > 0)

        # ────────────────────────────────────────────────────────────
        # 6.  RESPONSE
        # ────────────────────────────────────────────────────────────
        return Response({
            'summary': {
                'outside_factory_total': total_outside_factory,
                'active_items': active_items,
            },
            'status_vendors': ordered_status_vendors,
            'items': items,
            
            'totals': {
                'outside_factory': total_outside_factory,
                'status_vendor_totals': dict(status_vendor_totals),
                'status_totals' : dict(status_totals),
                'grand_total': grand_total,
            },
        })


class Dispatch(APIView):
    def get_permissions(self):
        return [IsAuthenticated(), HasAppPermission('stock.change_stockstatus')]

    def post(self, request):
        dispatch_status = request.data.get('destination_status')
        source_id = request.data.get('stock_id')
        dispatch_quantity = request.data.get('quantity')
        action = request.data.get('action')
        created_by = request.data.get('created_by')

        transporter = request.data.get('transporter')
        vehicle_number = request.data.get('vehicle_number')
        eta = request.data.get('eta')
        location = request.data.get('location')
    


        stock = StockStatus.objects.get(id=source_id)
        old_snapshot = {f: str(getattr(stock, f)) for f in TRACKED_FIELDS}

        new_record = dispatch(stock, dispatch_quantity, dispatch_status, created_by, transporter , eta , vehicle_number , location , action)

        create_audit(new_record, changed_by_label=created_by, action='CREATE', note=f"dispatched from #{source_id}")
        create_audit(stock, changed_by_label=created_by, action='UPDATE', old_snapshot=old_snapshot, note="dispatch source reduced")

        serializer = StockStatusSerializer(new_record)
        return Response(serializer.data)


class ArriveBatch(APIView):
    def get_permissions(self):
        return [IsAuthenticated(), HasAppPermission('stock.change_stockstatus')]

    def post(self, request):
        otw_id = request.data.get('stock_id')
        action = request.data.get('action')
        destination_status = request.data.get('destination_status')
        weighed_qty = request.data.get('weighed_qty')
        created_by = request.data.get('created_by')

        otw_record = StockStatus.objects.get(id=otw_id)
        old_snapshot = {f: str(getattr(otw_record, f)) for f in TRACKED_FIELDS}

        accumulator = arrive_batch(otw_record, weighed_qty, created_by, action, destination_status)

        create_audit(accumulator, changed_by_label=created_by, action='CREATE', note="batch arrival")
        create_audit(otw_record, changed_by_label=created_by, action='UPDATE', old_snapshot=old_snapshot, note="otw closed")

        serializer = StockStatusSerializer(accumulator)
        return Response(serializer.data)


class MoveView(APIView):
    def get_permissions(self):
        return [IsAuthenticated(), HasAppPermission('stock.view_stockstatus')]

    def post(self, request):
        stock_id = request.data.get('stock_id')
        new_quantity = request.data.get('new_quantity')
        action = request.data.get('action')
        created_by = request.data.get('created_by')
        new_status = request.data.get('new_status')
        arrival_date = request.data.get('arrival_date')
        stock = StockStatus.objects.get(id=stock_id)
        old_snapshot = {f: str(getattr(stock, f)) for f in TRACKED_FIELDS}

        new_record = move(stock, new_quantity, action, new_status, arrival_date, created_by)

        create_audit(new_record, changed_by_label=created_by, action='UPDATE', old_snapshot=old_snapshot, note=f"move → {new_status}")

        serializer = StockStatusSerializer(new_record)
        return Response(serializer.data)
    
class VehicleReport(APIView):
    def get_permissions(self):
        return [IsAuthenticated(), HasAppPermission('stock.view_vehicle_report')]

    def get(self, request):
        status = request.query_params.get('status')

        response = (
            StockStatus.objects.filter(
                status=status,
                deleted=False
            )
            .values(
                'vehicle_number',
                'transporter',       # ✅ added
                'item_code',
                'vendor_code',
                vendor_name=F('vendor_code__card_name'),
                item_name=F('item_code__tank_item_name'),
            )
            .annotate(
                total_quantity_in_litre=Sum('quantity_in_litre'),
                total_quantity_in_mts=Round(
                    ExpressionWrapper(
                        Sum('quantity_in_litre') / Decimal('1.0989') / 1000,
                        output_field=FloatField()
                    ), 3
                ),
                eta=Max('eta'),
                status=Max('status'),
                job_work=Max('job_work'),
                rate=Max('rate'),    # ✅ added
            )
            .order_by('vehicle_number', 'transporter', 'item_code')
        )

        grouped = {}
        for row in response:
            # ✅ use a proper tuple as the composite key
            group_key = (row['vehicle_number'], row['transporter'])

            if group_key not in grouped:
                grouped[group_key] = {
                    'vehicle_number': row['vehicle_number'],   # ✅ correct field
                    'transporter': row['transporter'],         # ✅ correct field
                    'items': []
                }

            grouped[group_key]['items'].append({
                'item_code': row['item_code'],
                'item_name': row['item_name'],
                'vendor_code': row['vendor_code'],
                'vendor_name': row['vendor_name'],
                'total_quantity_in_litre': row['total_quantity_in_litre'],
                'total_quantity_in_mts': row['total_quantity_in_mts'],
                'eta': row['eta'],
                'status': row['status'],
                'job_work': row['job_work'],
                'rate': row['rate'],    # ✅ added
            })

        return Response(list(grouped.values()))
    
# views.py
class StockChangeSessionListView(generics.ListAPIView):
    def get_permissions(self):
        return [IsAuthenticated(), HasAppPermission('stock.view_stockstatus')]
    
    serializer_class = StockStatusChangeSessionSerializer

    def get_queryset(self):
        queryset = StockStatusChangeSession.objects.prefetch_related('field_logs').order_by('-timestamp')
        stock_id = self.request.query_params.get('stock_id')
        if stock_id:
            queryset = queryset.filter(stock_id=stock_id)
        action = self.request.query_params.get('action')
        if action:
            queryset = queryset.filter(action=action)
        # filter by user — /api/stock/logs/?changed_by=harshit
        changed_by = self.request.query_params.get('changed_by')
        if changed_by:
            queryset = queryset.filter(changed_by_label=changed_by)
            
        return queryset


class OpeningStock(APIView):
    def get_permission(self):
        return [IsAuthenticated() , HasAppPermission('account.add_opening_rate')]
    
    def post(self , request):
        post_rate_liter = request.data.get('rate')
        item_code = request.data.get('item_code')
        quantity_liter = request.data.get('quantity')

        if not all([post_rate_liter, item_code, quantity_liter]):
            return Response(
                {'error': 'rate, item_code and quantity are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        tank_item = TankItem.objects.get(tank_item_code  = item_code)
        vendor = Party.objects.get(card_code = 'VENDA000004')
        quantity_in_kg = Decimal(str(quantity_liter)) / Decimal('1.0989')
        rate_kg = Decimal(str(post_rate_liter)) * Decimal('1.0989')

        StockStatus.objects.create(
            item_code = tank_item,
            status = 'IN_TANK',
            vendor_code = vendor,
            rate = rate_kg,
            quantity =  quantity_in_kg,
            location = 'Sonipat Factory'
        )

        return Response({f"Opening Rate for {tank_item} Updated"})
    
class DebitEntryListView(generics.ListAPIView):
    def get_permissions(self):
        return [IsAuthenticated() , HasAppPermission('stock.view_debitentry')]
    
    queryset = DebitEntry.objects.all()
    serializer_class = DebitEntrySerializer


class DebitEntryInsights(APIView):
    def get_permissions(self):
        return [IsAuthenticated() , HasAppPermission('stock.view_debitentry')]
    
    def get(self, request):
        insights = DebitEntry.objects.aggregate(
            total_deduction_shortager=Sum('deducted_shortage_qty'),
            total_records = Count('id'),
            total_deduction_amount=Sum('deduction_amount')
        )

        return Response(insights)


class ContractualHistoryListView(generics.ListAPIView):
    def get_permissions(self):
        return [IsAuthenticated() , HasAppPermission('stock.view_contractualhistory')]
    
    queryset = ContractualHistory.objects.all()
    serializer_class = ContractualHistorySerializer
    
class SnapshotListView(APIView):
    def get_permissions(self):
        return [IsAuthenticated() , HasAppPermission('stock.view_dashboardsnapshot')]
    
    def get(self, request):
        date  = request.query_params.get('date')
        if not date:
            return Response({"error": "date query parameter is required"}, status=400)

        snapshots = DashboardSnapshot.objects.filter(snapshot_date=date)
        serializer = DashboardSnapshotSerialixer(snapshots, many=True)
        return Response(serializer.data)        
