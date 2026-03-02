from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from datetime import date, timedelta
from collections import defaultdict
from django.http import JsonResponse

from .services import fetch_table_manually
from .models import DailyPrice
from.serializers import DailyPriceSerializer

class PriceFetchView(APIView):
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

    def post(self,request):
        data = fetch_table_manually()
        if isinstance(data,dict) and "error" in data:
            return Response(data , status= 400)

        print(data)
        for row in data:
            DailyPrice.objects.update_or_create(
                commodity_name = row['commodity_name'],
                date = row['fetched_date'],
                defaults = {
                    'factory_price': row['factory_kg'],
                    'packing_cost_kg': row['packing_kg'],
                    'with_gst_kg': row['gst_kg'],
                    'with_gst_ltr': row['gst_ltr'],
                }
            )

            return Response({"status": "Successfully posted to database"})


class DailyPriceTrend(APIView):
    def get(self,request):
        end_date = date.today()
        start_date = end_date - timedelta(days=7)

        prices = DailyPrice.objects.filter(
            date__range = [start_date , end_date]
        ).order_by('date')

        chart_data = defaultdict(list)
        unique_dates = []


        for p in prices:
            date_str = p.date.strftime('%b %d')
            if date_str not in unique_dates:
                unique_dates.append(date_str)

            chart_data[p.commodity_name].append(float(p.with_gst_ltr))

        datasets = []
        for commodity, values in chart_data.items():
            datasets.append({
                "label": commodity,
                "data": values,
                "fill": False
            })

        return JsonResponse({
            "labels": unique_dates,
            "datasets": datasets
        })
