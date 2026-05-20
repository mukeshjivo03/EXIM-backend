from .models import StockStatus, StockStatusUpdateLog, DebitEntry, StockStatusChangeSession, StockStatusFieldLog
from sap_sync.models import RMProducts, Party
from decimal import Decimal
from django.db import transaction


def resolve_parent(source):
    if source.can_be_parent:
        return source
    else:
        return source.parent


def get_or_create_accumulator(parent, new_status, arrived_qty, rate, created_by):
    existing = StockStatus.objects.filter(
        parent=parent,
        status=new_status,
        is_accumulator=True,
        deleted=False
    ).first()

    if existing:
        existing.quantity += arrived_qty
        existing.save()
        return existing
    else:
        return StockStatus.objects.create(
            item_code=parent.item_code,
            status=new_status,
            vendor_code=parent.vendor_code,
            rate=rate,
            quantity=arrived_qty,
            created_by=created_by,
            is_accumulator=True,
            parent=parent,
        )


def arrive_batch(otw_record, weighed_qty, created_by, action, destination_status):
    parent = resolve_parent(otw_record)
    accumulator = get_or_create_accumulator(parent, destination_status, weighed_qty, otw_record.rate, created_by)
    difference = otw_record.quantity - weighed_qty

    if difference != 0:
        if action == 'RETAIN':
            parent.quantity += difference
            parent.save()
        elif action == 'TOLERATE':
            pass
        elif action == 'DEBIT':
            if difference > 0:
                DebitEntry.objects.create(
                    stock=otw_record,
                    quantity=difference,
                    rate=otw_record.rate,
                    responsible_party=otw_record.vendor_code,
                    created_by=created_by,
                )

    otw_record.deleted = True
    otw_record.save()

    return accumulator


def dispatch(source, quantity, status, created_by, transporter , eta , vehicle_number , location  , action=None  ):
    if quantity > source.quantity:
        raise ValueError(f"Dispatch quantity {quantity} exceeds available quantity {source.quantity}")

    source.quantity -= quantity
    source.save()

    parent = resolve_parent(source)
    new_record = StockStatus.objects.create(
        item_code=source.item_code,
        status=status,
        vendor_code=source.vendor_code,
        rate=source.rate,
        quantity=quantity,
        created_by=created_by,
        parent=parent,
        
        transporter = transporter,
        vehicle_number = vehicle_number,
        eta = eta,
        location  = location
    )

    if action in ('TOLERATE', 'DEBIT'):
        if action == 'DEBIT':
            DebitEntry.objects.create(
                stock=source,
                quantity=source.quantity,
                rate=source.rate,
                responsible_party=source.vendor_code,
                created_by=created_by,
            )

        active_children = StockStatus.objects.filter(
            parent=parent,
            deleted=False,
        ).exclude(id=new_record.id)

        if active_children.exists():
            source.quantity = 0
            source.save()
        else:
            source.deleted = True
            source.save()

    return new_record


def move(source, new_quantity, action, new_status, created_by):
    difference = Decimal(source.quantity) - Decimal(new_quantity)
    print(source)

    if difference != 0:
        if action == 'RETAIN':
            parent = resolve_parent(source)
            print(parent)

            if not parent or parent.deleted or parent.id == source.id:
                raise ValueError("Cannot RETAIN — no valid storage parent exists.")
            parent.quantity += difference
            parent.save()

        if action == 'TOLERATE':
            source.status = new_status
            source.quantity = new_quantity
            
            print(source)
            
            if new_status == 'IN_TANK' and not source.bility_number:
                raise ValueError("Bility number is required when status is IN_TANK.")

        elif action == 'DEBIT':
            DebitEntry.objects.create(
                stock=source,
                quantity=difference,
                rate=source.rate,
                responsible_party=source.vendor_code,
                created_by=created_by,
            )
            source.status = new_status

    source.quantity = new_quantity
    source.status = new_status
    source.save()

    return source


# ── Audit ──────────────────────────────────────────────────────────────────

TRACKED_FIELDS = ['status', 'rate', 'quantity', 'vehicle_number', 'location', 'eta']


def create_audit(stock, changed_by_label, action, old_snapshot=None, note=''):
    with transaction.atomic():
        session = StockStatusChangeSession.objects.create(
            stock=stock,
            action=action,
            changed_by_label=changed_by_label,
            note=note,
        )

        if action == 'CREATE':
            StockStatusFieldLog.objects.create(
                session=session,
                field_name='__create__',
                old_value=None,
                new_value={f: str(getattr(stock, f)) for f in TRACKED_FIELDS},
            )

        elif action == 'UPDATE' and old_snapshot:
            changed = [
                (f, old_snapshot[f], str(getattr(stock, f)))
                for f in TRACKED_FIELDS
                if old_snapshot.get(f) != str(getattr(stock, f))
            ]
            if changed:
                StockStatusFieldLog.objects.bulk_create([
                    StockStatusFieldLog(session=session, field_name=f, old_value=old_v, new_value=new_v)
                    for f, old_v, new_v in changed
                ])

        return session