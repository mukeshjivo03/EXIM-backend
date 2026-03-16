from django.db import transaction
from decimal import Decimal
from .models import TankData, TankLayer, TankLog, TankLogConsumption
from stock.models import StockStatus


class TankService:

    @staticmethod
    @transaction.atomic
    def inward(tank_code, stock_status_id, quantity, created_by):
        
        """
        Oil goes INTO the tank.
        Full flow in one atomic transaction:
        1. Validate tank space and item match
        2. Handle stock split if quantity < stock entry quantity
        3. Update original stock entry status to IN_TANK
        4. Create TankLayer
        5. Create TankLog
        6. Update tank current_capacity
        """
        
        tank = TankData.objects.select_for_update().get(tank_code=tank_code)
        stock_entry = StockStatus.objects.select_for_update().get(pk=stock_status_id)

        # --- Validations ---
        # Tank has enough space
        
        available_space = tank.tank_capacity - (tank.current_capacity or Decimal('0.00'))
        if quantity > available_space:
            raise ValueError(
                f"Tank {tank_code} only has {available_space} MT space. Cannot add {quantity} MT."
            )

        # Quantity cannot exceed stock entry quantity
        if quantity > stock_entry.quantity:
            raise ValueError(
                f"Stock entry #{stock_entry.pk} only has {stock_entry.quantity} MT. Cannot add {quantity} MT."
            )

        # Item must match tank's item
        if tank.item_code and stock_entry.item_code and tank.item_code != stock_entry.item_code:
            raise ValueError(
                f"Tank {tank_code} holds {tank.item_code}. Cannot add {stock_entry.item_code}."
            )

        # Stock entry must be OUTSIDE_FACTORY
        if stock_entry.status != 'OUT_SIDE_FACTORY':
            raise ValueError(
                f"Stock entry #{stock_entry.pk} has status '{stock_entry.status}'. Expected 'OUT_SIDE_FACTORY'."
            )

        # --- Stock Split Logic ---

        remainder = stock_entry.quantity - quantity

        if remainder > Decimal('0.00'):
            # Partial quantity — create a new entry with the leftover
            StockStatus.objects.create(
                item_code=stock_entry.item_code,
                status='OUT_SIDE_FACTORY',
                vendor_code=stock_entry.vendor_code,
                rate=stock_entry.rate,
                quantity=remainder,
                created_by=created_by,
            )

        # Update original stock entry — quantity becomes what went into tank, status becomes IN_TANK
        stock_entry.quantity = quantity
        stock_entry.status = 'IN_TANK'
        stock_entry.save()

        # --- Create Tank Layer ---

        layer = TankLayer.objects.create(
            tank_code=tank,
            stock_status=stock_entry,
            item_code=stock_entry.item_code,
            vendor=stock_entry.vendor_code,
            rate=stock_entry.rate,
            quantity_added=quantity,
            quantity_remaining=quantity,
            created_by=created_by,
        )

        # --- Create Tank Log ---

        log = TankLog.objects.create(
            tank_code=tank,
            log_type='INWARD',
            quantity=quantity,
            stock_status=stock_entry,
            tank_layer=layer,
            created_by=created_by,
        )

        # --- Update Tank Capacity ---
        if tank.item_code is None:
            tank.item_code = stock_entry.item_code
            tank.save()

        tank.current_capacity = (tank.current_capacity or Decimal('0.00')) + quantity
        tank.save()

        return {
            'layer': layer,
            'log': log,
            'stock_split': remainder > Decimal('0.00'),
            'remainder_quantity': remainder,
        }

    @staticmethod
    @transaction.atomic
    def outward(tank_code, quantity, created_by, remarks=''):
        """
        Oil goes OUT of the tank (production consumption).
        FIFO: eats oldest layers first, records cost trail.
        """
        tank = TankData.objects.select_for_update().get(tank_code=tank_code)

        # Validate: tank has enough oil
        current = tank.current_capacity or Decimal('0.00')
        if quantity > current:
            raise ValueError(
                f"Tank {tank_code} only has {current} MT. Cannot withdraw {quantity} MT."
            )

        # Create the outward log first
        log = TankLog.objects.create(
            tank_code=tank,
            log_type='OUTWARD',
            quantity=quantity,
            created_by=created_by,
            remarks=remarks,
        )

        # FIFO consumption
        remaining_to_consume = quantity

        # Get all active layers, ordered by id (oldest first = FIFO)
        layers = (
            TankLayer.objects
            .filter(tank_code=tank, is_exhausted=False)
            .order_by('id')
            .select_for_update()
        )

        for layer in layers:
            if remaining_to_consume <= Decimal('0.00'):
                break

            # Get rate from the linked stock status
            layer_rate = layer.stock_status.rate if layer.stock_status else Decimal('0.00')

            if layer.quantity_remaining <= remaining_to_consume:
                # This layer is fully consumed
                consumed = layer.quantity_remaining
                layer.quantity_remaining = Decimal('0.00')
                layer.is_exhausted = True
            else:
                # Partially consumed — this layer still has oil left
                consumed = remaining_to_consume
                layer.quantity_remaining -= consumed

            layer.save()

            # Record the consumption trail (rate is snapshot — won't change even if stock entry is edited later)
            TankLogConsumption.objects.create(
                tank_log=log,
                tank_layer=layer,
                quantity_consumed=consumed,
                rate=layer_rate,
            )

            remaining_to_consume -= consumed

        # Update tank current capacity
        tank.current_capacity = current - quantity
        tank.save()

        return {
            'log': log,
            'consumptions': list(log.consumptions.all()),
            'cost_breakdown': TankService.get_outward_cost_breakdown(log),
        }

    @staticmethod
    def get_outward_cost_breakdown(tank_log):
        """
        For any outward log, returns the FIFO cost breakdown.
        """
        consumptions = tank_log.consumptions.select_related(
            'tank_layer__stock_status__vendor_code'
        ).all()

        total_cost = Decimal('0.00')
        total_qty = Decimal('0.00')
        breakdown = []

        for c in consumptions:
            line_cost = c.quantity_consumed * c.rate
            total_cost += line_cost
            total_qty += c.quantity_consumed

            stock = c.tank_layer.stock_status
            breakdown.append({
                'layer_id': c.tank_layer.id,
                'stock_status_id': stock.pk if stock else None,
                'vendor': str(stock.vendor_code) if stock else 'N/A',
                'quantity': c.quantity_consumed,
                'rate': c.rate,
                'line_cost': line_cost,
            })

        weighted_avg_rate = (total_cost / total_qty) if total_qty > 0 else Decimal('0.00')

        return {
            'breakdown': breakdown,
            'total_quantity': total_qty,
            'total_cost': total_cost,
            'weighted_avg_rate': weighted_avg_rate,
        }

    @staticmethod
    def get_tank_status(tank_code):
        """
        Current state of a tank — active layers with cost breakdown.
        """
        layers = (
            TankLayer.objects
            .filter(tank_code=tank_code, is_exhausted=False)
            .order_by('id')
            .select_related('stock_status__vendor_code', 'stock_status__item_code')
        )

        total_qty = Decimal('0.00')
        total_cost = Decimal('0.00')
        layer_data = []

        for layer in layers:
            stock = layer.stock_status
            rate = stock.rate if stock else Decimal('0.00')
            line_cost = layer.quantity_remaining * rate

            total_qty += layer.quantity_remaining
            total_cost += line_cost

            layer_data.append({
                'layer_id': layer.id,
                'stock_status_id': stock.pk if stock else None,
                'vendor': str(stock.vendor_code) if stock else 'N/A',
                'item': str(stock.item_code) if stock else 'N/A',
                'rate': rate,
                'quantity_remaining': layer.quantity_remaining,
                'quantity_added': layer.quantity_added,
                'line_cost': line_cost,
                'created_at': layer.created_at,
            })

        weighted_avg_rate = (total_cost / total_qty) if total_qty > 0 else Decimal('0.00')

        return {
            'layers': layer_data,
            'total_quantity': total_qty,
            'total_cost': total_cost,
            'weighted_avg_rate': weighted_avg_rate,
        }