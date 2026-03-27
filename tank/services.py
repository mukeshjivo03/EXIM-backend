from django.db import transaction
from decimal import Decimal
from .models import TankData, TankLayer, TankLog, TankLogConsumption
from stock.models import StockStatus
from django.db.models import Sum



class TankService:

    @staticmethod
    @transaction.atomic
    def inward(tank_code, stock_status_id, quantity, created_by):
        
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
        if quantity > stock_entry.quantity_in_litre:
            raise ValueError(
                f"Stock entry #{stock_entry.pk} only has {stock_entry.quantity_in_litre} MT. Cannot add {quantity} MT."
            )

        # Item must match tank's item
        if tank.item_code and stock_entry.item_code and tank.item_code != stock_entry.item_code:
            raise ValueError(
                f"Tank {tank_code} holds {tank.item_code}. Cannot add {stock_entry.item_code}."
            )

        # Stock entry must be OUTSIDE_FACTORY
        if stock_entry.status != 'COMPLETED':
            raise ValueError(
                f"Stock entry #{stock_entry.pk} has status '{stock_entry.status}'. Expected 'COMPLETED'."
            )

        # --- Stock Split Logic ---

        remainder = stock_entry.quantity_in_litre - quantity
        quantity_remaining_in_kg = remainder / Decimal('1.0989')
        quantity_in_tank_in_kg = quantity / Decimal('1.0989')
        


        if remainder > Decimal('0.00'):
            # Partial quantity — create a new entry with the leftover
            StockStatus.objects.create(
                item_code=stock_entry.item_code,
                status='OUT_SIDE_FACTORY',
                vendor_code=stock_entry.vendor_code,
                rate=stock_entry.rate,
                quantity=quantity_remaining_in_kg,
                vehicle_number = stock_entry.vehicle_number,
                transporter = stock_entry.transporter,
                created_by=created_by,
            )

        # Update original stock entry — quantity becomes what went into tank, status becomes IN_TANK
        stock_entry.quantity = quantity_in_tank_in_kg
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
        Updates StockStatus quantity (KG) as oil is consumed.
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

        # Track consumption per stock_status
        stock_consumed_litres = {}  # {stock_status_id: total_litres_consumed}

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

            # Record the consumption trail
            TankLogConsumption.objects.create(
                tank_log=log,
                tank_layer=layer,
                quantity_consumed=consumed,
                rate=layer_rate,
            )

            # Accumulate per stock_status
            if layer.stock_status_id:
                stock_consumed_litres[layer.stock_status_id] = (
                    stock_consumed_litres.get(layer.stock_status_id, Decimal('0.00')) + consumed
                )

            remaining_to_consume -= consumed

        # --- Update each touched StockStatus (mirror of inward split logic) ---
        for stock_id, consumed_litres in stock_consumed_litres.items():
            stock = StockStatus.objects.select_for_update().get(pk=stock_id)

            # Convert litres back to KG (same factor used in inward)
            consumed_kg = consumed_litres / Decimal('1.0989')
            stock.quantity = max(stock.quantity - consumed_kg, Decimal('0.00'))

            # If all layers for this stock are done → COMPLETED
            has_active_layers = TankLayer.objects.filter(
                stock_status_id=stock_id, is_exhausted=False
            ).exists()

            if not has_active_layers:
                stock.status = 'COMPLETED'
                stock.deleted = True

            stock.save()  # triggers quantity_in_litre recalc + update log

        # Update tank current capacity
        tank.current_capacity = current - quantity
        tank.save()

        return {
            'log': log,
            'consumptions': list(log.consumptions.all()),
            'cost_breakdown': TankService.get_outward_cost_breakdown(log),
        }
        
    @staticmethod
    @transaction.atomic
    def transfer(source_tank_code, destination_tank_code, quantity, created_by, remarks=''):
        """
        Transfer oil from one tank to another.
        FIFO: consumes oldest layers from source, creates new layers in destination.
        """
        source_tank = TankData.objects.select_for_update().get(tank_code=source_tank_code)
        destination_tank = TankData.objects.select_for_update().get(tank_code=destination_tank_code)

        # --- Validations ---

        if source_tank_code == destination_tank_code:
            raise ValueError("Source and destination tank cannot be the same.")

        # Source tank has enough oil
        source_current = source_tank.current_capacity or Decimal('0.00')
        if quantity > source_current:
            raise ValueError(
                f"Tank {source_tank_code} only has {source_current} MT. Cannot transfer {quantity} MT."
            )

        # Destination tank has enough space
        dest_available = destination_tank.tank_capacity - (destination_tank.current_capacity or Decimal('0.00'))
        if quantity > dest_available:
            raise ValueError(
                f"Tank {destination_tank_code} only has {dest_available} MT space. Cannot transfer {quantity} MT."
            )

        # Item code must match or destination must be empty
        if destination_tank.item_code and source_tank.item_code and destination_tank.item_code != source_tank.item_code:
            raise ValueError(
                f"Tank {destination_tank_code} holds {destination_tank.item_code}. Cannot transfer {source_tank.item_code}."
            )

        # --- Create Transfer Log ---

        log = TankLog.objects.create(
            tank_code=source_tank,
            destination_tank=destination_tank,
            log_type='TRANSFER',
            quantity=quantity,
            created_by=created_by,
            remarks=remarks,
        )

        # --- FIFO consumption from source & layer creation in destination ---

        remaining_to_transfer = quantity

        layers = (
            TankLayer.objects
            .filter(tank_code=source_tank, is_exhausted=False)
            .order_by('id')
            .select_for_update()
        )

        for layer in layers:
            if remaining_to_transfer <= Decimal('0.00'):
                break

            if layer.quantity_remaining <= remaining_to_transfer:
                consumed = layer.quantity_remaining
                layer.quantity_remaining = Decimal('0.00')
                layer.is_exhausted = True
            else:
                consumed = remaining_to_transfer
                layer.quantity_remaining -= consumed

            layer.save()

            # Record consumption trail on source
            TankLogConsumption.objects.create(
                tank_log=log,
                tank_layer=layer,
                quantity_consumed=consumed,
                rate=layer.rate,
            )

            # Create new layer in destination tank with same data
            TankLayer.objects.create(
                tank_code=destination_tank,
                stock_status=layer.stock_status,
                item_code=layer.item_code,
                vendor=layer.vendor,
                rate=layer.rate,
                quantity_added=consumed,
                quantity_remaining=consumed,
                created_by=created_by,
            )

            remaining_to_transfer -= consumed

        # --- Update Tank Capacities ---

        source_item_code = source_tank.item_code

        source_tank.current_capacity = source_current - quantity
        if source_tank.current_capacity == Decimal('0.00'):
            source_tank.item_code = None
        source_tank.save()

        if destination_tank.item_code is None:
            destination_tank.item_code = source_item_code
        destination_tank.current_capacity = (destination_tank.current_capacity or Decimal('0.00')) + quantity
        destination_tank.save()

        return {
            'log': log,
            'consumptions': list(log.consumptions.all()),
            'source_tank': source_tank_code,
            'destination_tank': destination_tank_code,
            'quantity_transferred': quantity,
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
        


def ItemAvergaCost(itemCode):
    
    total_tank_capacity = TankData.objects.filter(item_code=itemCode).aggregate(total_capacity=Sum('current_capacity'))['total_capacity']
    stockRecords = StockStatus.objects.filter(item_code=itemCode , deleted = False ,status ='IN_TANK').order_by('created_at').only('quantity_in_litre' , 'rate' ,  'created_at')

    remaining = total_tank_capacity
    weighted_sum = Decimal('0.00')
    stock_status_quantity = Decimal('0.00')
    breakdown = []
    
    for record in stockRecords:
        if remaining <= 0:
            break
    
        consumed = min(record.quantity_in_litre , remaining)
        weighted_sum +=  record.rate * record.quantity_in_litre
        stock_status_quantity += record.quantity_in_litre
        remaining -= consumed
        
        breakdown.append({
            'stock_id':          record.pk,
            'created_at':        record.created_at,
            'rate':              record.rate,
            'batch_quantity':    record.quantity,
            'quantity_consumed': consumed,
            'batch_total':       consumed * record.rate,
        })
    
    quantity_matched = total_tank_capacity - remaining
    quantity_unmatched = remaining
    
    if quantity_matched == Decimal('0.00'):
        return {
            'item_code' : itemCode,
            'tank_total_capacity' : total_tank_capacity,
            'quantity_matched' : quantity_matched,
            'quantity_unmatched' : quantity_unmatched,
            'average_rate' : Decimal('0.00'),
            'warning': (
                'Tank has capacity but no IN_TANK stock records found. '
                'Average cost cannot be computed.'
            ),
            
        }
        
    print(weighted_sum)
    average_rate = (weighted_sum / total_tank_capacity).quantize(Decimal('0.01'))
    adjusted_average = (weighted_sum / quantity_matched).quantize(Decimal('0.01'))
    warning = None
    if quantity_unmatched > Decimal('0.00'):
        warning = (
            f'{quantity_unmatched} units of tank capacity could not be matched '
            f'to any IN_TANK stock record. Average is partial.'
        )

    return {
        'item_code':           itemCode,
        'tank_total_capacity': total_tank_capacity,
        'quantity_matched':    quantity_matched,
        'quantity_unmatched':  quantity_unmatched,
        'average_rate(IN_TANK)':        average_rate,
        'adjusted_average(STO)':    adjusted_average,
        'warning':             warning,
    }
    
   
        