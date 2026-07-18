from django.shortcuts import render
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import PackingMargins , CommodityMargin , MarketRates , BasicRates , PackSize , PackRates
from .serializers import  PackingMarginSerializer , CommodityMarginSerializer , MarketRateCreateSerializer ,MarketRatesViewSerializer ,BasicRatesSerializer , PackSizeSerializer , PackRatesSerializer


class PackingMarginListCreateView(generics.ListCreateAPIView):
    queryset = PackingMargins.objects.all()
    serializer_class = PackingMarginSerializer

class PackingMarginRetrieveUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    queryset = PackingMargins.objects.all()
    serializer_class = PackingMarginSerializer
    lookup_field = 'id'

class CommodityMarginListCreateView(generics.ListCreateAPIView):
    queryset = CommodityMargin.objects.all()
    serializer_class = CommodityMarginSerializer

class MarketRateCreateView(generics.CreateAPIView):
    queryset = MarketRates.objects.all()
    serializer_class = MarketRateCreateSerializer

class MarketRateRetrieveUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    queryset = MarketRates.objects.all()
    serializer_class = MarketRatesViewSerializer
    lookup_field = 'id'

class MarketRatesGetView(generics.ListAPIView):
    queryset = MarketRates.objects.all()
    serializer_class = MarketRatesViewSerializer
    def get_queryset(self):
        queryset = super().get_queryset()
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')

        if start_date and end_date:
            queryset = queryset.filter(date__range=[start_date, end_date])
        return queryset



class GetLatestMarketRates(APIView):
    def get(self , request):
        latest_rates = MarketRates.objects.order_by('commodity_id', '-date').distinct('commodity_id')
        serializer  = MarketRatesViewSerializer(latest_rates, many = True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class GetBasicRatesView(APIView):
    def get(self , request):
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')

        if start_date and end_date:
            data = BasicRates.objects.filter(date__range=[start_date, end_date])
        else:
            data = BasicRates.objects.all()

        serializer = BasicRatesSerializer(data , many = True)
        return Response({"basic_rates" : serializer.data})


class PackSizeListCreateView(generics.ListCreateAPIView):
    queryset = PackSize.objects.all()
    serializer_class = PackSizeSerializer

class PackSizeRetrieveUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    queryset = PackSize.objects.all()
    serializer_class = PackSizeSerializer
    lookup_field = 'id'


class GetPackRatesView(APIView):
    def get(self, request):
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')

        queryset = PackRates.objects.select_related('pack_size', 'market_rate__commodity')
        if start_date and end_date:
            queryset = queryset.filter(date__range=[start_date, end_date])

        serializer = PackRatesSerializer(queryset, many=True)
        return Response({"pack_rates": serializer.data})


class GetLatestRateTableView(APIView):
    """Pivoted rate table: one row per pack size, one column per commodity,
    built from the latest market rate of each commodity."""
    def get(self, request):
        latest_rates = MarketRates.objects.order_by('commodity_id', '-date', '-id').distinct('commodity_id')
        latest_ids = [rate.id for rate in latest_rates]

        pack_rates = PackRates.objects.filter(market_rate_id__in=latest_ids).select_related(
            'pack_size', 'market_rate__commodity'
        )

        commodities = []
        rows = {}
        for pack_rate in pack_rates:
            if pack_rate.pack_size is None or pack_rate.market_rate.commodity is None:
                continue
            commodity = pack_rate.market_rate.commodity.commodity
            if commodity not in commodities:
                commodities.append(commodity)

            pack_size = pack_rate.pack_size
            row = rows.setdefault(pack_size.id, {
                "pack_size": pack_size.name,
                "display_order": pack_size.display_order,
                "rates": {},
            })
            row["rates"][commodity] = pack_rate.rate

        sorted_rows = sorted(rows.values(), key=lambda r: (r.pop("display_order"), r["pack_size"]))

        return Response({
            "commodities": commodities,
            "rows": sorted_rows,
        })


