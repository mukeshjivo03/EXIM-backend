from django.core.management.base import BaseCommand
from daily_price.services import fetch_table_manually , fetch_jivo_rates
from daily_price.models import DailyPrice , JivoRates


class Command(BaseCommand):
    help = 'Fetches today\'s rates from Google Sheets and saves to DB'

    def handle(self,*args,**kwargs):
        self.stdout.write("Fetching data from Google Sheets...")
        daily_price_data = fetch_table_manually()
        jivo_rates_data = fetch_jivo_rates()
        
        if not daily_price_data or (isinstance(daily_price_data, dict) and "error" in daily_price_data):
            self.stdout.write(self.style.ERROR("Failed to fetch data or table not found."))
            return

        for row in daily_price_data:
            obj, created = DailyPrice.objects.update_or_create(
                commodity_name=row['commodity_name'],
                date=row['fetched_date'],
                defaults={
                    'factory_price': row['factory_kg'],
                    'packing_cost_kg': row['packing_kg'],
                    'with_gst_kg': row['gst_kg'],
                    'with_gst_ltr': row['gst_ltr'],
                    'craeted_by': 'System'
                }
            )
            status = "Created" if created else "Updated"
            self.stdout.write(f"{status}: {row['commodity_name']}")
            
        if not jivo_rates_data or (isinstance(jivo_rates_data, dict) and "error" in jivo_rates_data):
            self.stdout.write(self.style.ERROR("Failed to fetch Jivo Rates data or table not found."))
            return
        
        for row in jivo_rates_data:
            obj, created = JivoRates.objects.update_or_create(
                pack_type=row['pack_type'],
                commodity=row['commodity'],
                date=row['date'],
                defaults={
                    'rate': row['rate'],
                    'created_by': 'System'
                }
            )
            
            status = "Created" if created else "Updated"
            self.stdout.write(f"{status}: {row['commodity']}")
            

        self.stdout.write(self.style.SUCCESS("Successfully synced all rates."))
        
        
