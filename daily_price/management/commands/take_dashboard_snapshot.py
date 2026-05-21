from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db.models import Sum
from stock.models import StockStatus, DashboardSnapshot  # adjust app name


class Command(BaseCommand):
    help = "Takes a daily snapshot of the dashboard (item × status × vendor)"

    def handle(self, *args, **kwargs):
        self._take_snapshot()

    def _take_snapshot(self):
        snapshot_date = timezone.now().date()
        self.stdout.write(f"Taking dashboard snapshot for {snapshot_date}...")

        if DashboardSnapshot.objects.filter(snapshot_date=snapshot_date).exists():
            self.stdout.write(self.style.WARNING(
                f"Snapshot for {snapshot_date} already exists. Skipping."
            ))
            return

        qs = (
            StockStatus.objects
            .filter(deleted=False)
            .select_related('item_code', 'vendor_code')
            .values(
                'item_code__tank_item_code',
                'item_code__tank_item_name',      # adjust to your TankItem field
                'status',
                'vendor_code__card_code',    # adjust to your Party field
                'vendor_code__card_name',    # adjust to your Party field
            )
            .annotate(total_qty=Sum('quantity'))
        )

        if not qs.exists():
            self.stdout.write(self.style.WARNING("No StockStatus records found. Nothing to snapshot."))
            return

        snapshots = []
        for row in qs:
            snapshots.append(DashboardSnapshot(
                snapshot_date=snapshot_date,
                item_code=row['item_code__tank_item_code'],
                item_name=row['item_code__tank_item_name'] or '',
                status=row['status'],
                vendor_code =row['vendor_code__card_code'] or 'UNKNOWN',
                vendor_name=row['vendor_code__card_name'] or 'UNKNOWN',
                quantity=row['total_qty'],
            ))
            self.stdout.write(
                f"  Queued: {row['item_code__tank_item_code']} | {row['status']} | {row['vendor_code__card_name']}"
            )

        DashboardSnapshot.objects.bulk_create(snapshots)
        self.stdout.write(self.style.SUCCESS(
            f"Snapshot for {snapshot_date} saved — {len(snapshots)} rows."
        ))