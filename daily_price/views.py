from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from datetime import date, timedelta
from collections import defaultdict
from django.http import JsonResponse
from django_filters.rest_framework import DjangoFilterBackend

from .services import fetch_table_manually , fetch_jivo_rates
from .models import DailyPrice , JivoRates
from.serializers import DailyPriceSerializer , JivoRatesSerializer
from accounts.permissions import HasAppPermission

class DailyPriceListView(generics.ListAPIView):
    def get_permissions(self):
        return [IsAuthenticated(), HasAppPermission('daily_price.view_dailyprice')]

    queryset = DailyPrice.objects.all()
    serializer_class = DailyPriceSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['date']


class PriceFetchView(APIView):
    def get_permissions(self):
        if self.request.method == "POST":
            return [IsAuthenticated(), HasAppPermission("daily_price.add_dailyprice")]
        
        return [
            IsAuthenticated(), 
            HasAppPermission("daily_price.fetch_daily_price"), 
            HasAppPermission("daily_price.view_dailyprice")
        ]
    def get(self, request):
        data = fetch_table_manually()
        if not data:
            return Response({
                "error": "Table not found. Check if 'Commodities' cell exists in the sheet."
            }, status=404)
        
        return Response({
            "status": "success",
            "count": len(data),
            "preview_data": data
        })

    def post(self, request):
        data = fetch_table_manually()
        if isinstance(data, dict) and "error" in data:
            return Response(data, status=400)
    
        print(data)
        for row in data:
            DailyPrice.objects.update_or_create(
                commodity_name=row['commodity_name'],
                date=row['fetched_date'],
                defaults={
                    'factory_price': row['factory_kg'],
                    'packing_cost_kg': row['packing_kg'],
                    'with_gst_kg': row['gst_kg'],
                    'with_gst_ltr': row['gst_ltr'],
                }
            )
    
        # Move this outside the loop!
        return Response({"status": f"Successfully processed {len(data)} rows"})


class DailyPriceTrend(APIView):
    def get_permissions(self):
        return [IsAuthenticated(), HasAppPermission('daily_price.view_daily_price_graph')]
    def get(self,request):
        
        end_date = request.query_params.get('end_date')
        start_date = request.query_params.get('start_date')

        prices = DailyPrice.objects.filter(
            date__range = [start_date , end_date]
        ).order_by('date')

        chart_data = defaultdict(list)
        unique_dates = []


        for p in prices:
            date_str = p.date.strftime('%b %d')
            if date_str not in unique_dates:
                unique_dates.append(date_str)

            chart_data[p.commodity_name].append(float(p.with_gst_kg))

        datasets = []
        for commodity, values in chart_data.items():
            datasets.append({
                "label": commodity,
                "data": values,
            })

        return JsonResponse({
            "labels": unique_dates,
            "datasets": datasets
        })
        
        
class DailyPriceRangeView(APIView):
    def get_permissions(self):
        return [IsAuthenticated(), HasAppPermission('daily_price.view_dailyprice')]
    def get(self, request):
        from_date = request.query_params.get('from_date')
        to_date = request.query_params.get('to_date')
        
        if not from_date or not to_date:
            return Response({'error': 'Both from_date and to_date are required.'}, status=400)
        
        result = DailyPrice.objects.filter(date__range=[from_date, to_date])
        serialized = DailyPriceSerializer(result, many=True)
        return Response(serialized.data)
    
    
class JivoRatesFetch(APIView):
    def get_permissions(self):
        if self.request.method == "POST":
            return [IsAuthenticated(), HasAppPermission('daily_price.add_jivorates'), HasAppPermission('daily_price.view_jivorates')]
        
        return [IsAuthenticated() , HasAppPermission('daily_price.fetch_jivo_rates')]

    def get(self, request):
        data = fetch_jivo_rates()
        
        if not data:
            return Response({
                "error": "Table not found. Check if 'Commodities' cell exists in the sheet."
            }, status=404)
        
        return Response({
            "status": "success",
            "count": len(data),
            "preview_data": data
        })
            
    def post(self, request):
        data = fetch_jivo_rates()
        createdBy = request.data.get('created_by')
        
        if isinstance(date,dict) and "error" in data:
            return Response(data, status=400)
        print(data)
        for row in data:
            JivoRates.objects.update_or_create(
                pack_type=row['pack_type'],
                commodity=row['commodity'],
                date=row['date'],
                created_by=createdBy,
                defaults={
                    'rate': row['rate'],
                }
            )
        return Response({"status": f"Successfully processed {len(data)} rows"})
    
    
class JivoRatesWithRange(APIView):
    def get_permissions(self):
        return  [IsAuthenticated(), HasAppPermission('daily_price.view_jivorates')]

    def get(self, request):
        from_date = request.query_params.get('from_date')
        to_date = request.query_params.get('to_date')
        
        if not from_date or not to_date:
            raise ValueError('Both from_date and to_date are required.')
        
        result = JivoRates.objects.filter(date__range=[from_date , to_date])
        serialized = JivoRatesSerializer(result , many = True)
        return Response(serialized.data)
    
    