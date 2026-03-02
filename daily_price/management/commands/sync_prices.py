from django.core.management.base import BaseCommand
from daily_price.services import fetch_table_manually
from daily_price.models import DailyPrice

class Command(BaseCommand):
    help = 'Fetches today\'s rates from Google Sheets and saves to DB'

    def handle(self,*args,**kwargs):
        self.stdout.write("Fetching data from Google Sheets...")
        data = fetch_table_manually()

        if not data or (isinstance(data, dict) and "error" in data):
            self.stdout.write(self.style.ERROR("Failed to fetch data or table not found."))
            return

        for row in data:
            obj, created = DailyPrice.objects.update_or_create(
                commodity_name=row['commodity_name'],
                date=row['fetched_date'],
                defaults={
                    'factory_price': row['factory_kg'],
                    'packing_cost_kg': row['packing_kg'],
                    'with_gst_kg': row['gst_kg'],
                    'with_gst_ltr': row['gst_ltr'],
                }
            )
            status = "Created" if created else "Updated"
            self.stdout.write(f"{status}: {row['commodity_name']}")

        self.stdout.write(self.style.SUCCESS("Successfully synced all rates."))