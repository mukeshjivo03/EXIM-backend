from django.core.management.base import BaseCommand
from daily_price.services import fetch_table_manually, fetch_jivo_rates
from daily_price.models import DailyPrice, JivoRates


class Command(BaseCommand):
    help = "Fetches today's rates from Google Sheets and saves to DB"

    def handle(self, *args, **kwargs):
        self._sync_daily_prices()
        self._sync_jivo_rates()
        self.stdout.write(self.style.SUCCESS("Successfully synced all rates."))

    def _sync_daily_prices(self):
        self.stdout.write("Fetching Daily Price data from Google Sheets...")
        try:
            data = fetch_table_manually()
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Exception while fetching daily prices: {e}"))
            return

        if not data or (isinstance(data, dict) and "error" in data):
            self.stdout.write(self.style.ERROR("Failed to fetch daily price data or table not found."))
            return

        for row in data:
            _, created = DailyPrice.objects.update_or_create(
                commodity_name=row['commodity_name'],
                date=row['fetched_date'],
                defaults={
                    'factory_price': row['factory_kg'],
                    'packing_cost_kg': row['packing_kg'],
                    'with_gst_kg': row['gst_kg'],
                    'with_gst_ltr': row['gst_ltr'],
                    'created_by': 'System',   # fixed typo: craeted_by -> created_by
                }
            )
            status = "Created" if created else "Updated"
            self.stdout.write(f"  {status}: {row['commodity_name']}")

    def _sync_jivo_rates(self):
        self.stdout.write("Fetching Jivo Rates data from Google Sheets...")
        try:
            data = fetch_jivo_rates()
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Exception while fetching Jivo rates: {e}"))
            return

        if not data or (isinstance(data, dict) and "error" in data):
            self.stdout.write(self.style.ERROR("Failed to fetch Jivo Rates data or table not found."))
            return

        for row in data:
            _, created = JivoRates.objects.update_or_create(
                pack_type=row['pack_type'],
                commodity=row['commodity'],
                date=row['date'],
                defaults={
                    'rate': row['rate'],
                    'created_by': 'System',
                }
            )
            status = "Created" if created else "Updated"
            self.stdout.write(f"  {status}: {row['commodity']}")