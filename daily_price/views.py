from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response

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