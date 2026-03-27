from django.db import models
from django.db import models, transaction

# Create your models here.
class TankItem(models.Model):
    tank_item_code = models.CharField(unique=True ,max_length=50 , primary_key = True)
    tank_item_name = models.CharField(max_length = 255)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.CharField(max_length=50)
    color = models.CharField(max_length=10)
    
    class Meta:
        db_table = 'tank_item'
        
    def __str__(self):
        return self.tank_item_name
    

class TankData(models.Model):

    tank_code = models.CharField(primary_key=True, max_length=20, editable=False)
    item_code = models.ForeignKey('TankItem', on_delete=models.SET_NULL, null=True)      
    tank_capacity = models.DecimalField(max_digits=10, decimal_places=2)
    current_capacity = models.DecimalField(blank=True, null=True, max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'tank_data'
        
    def save(self, *args, **kwargs):
        if not self.tank_code:
            with transaction.atomic(): 
                existing_tanks = TankData.objects.select_for_update().values_list('tank_code', flat=True)
                existing_numbers = set()

                for code in existing_tanks:
                    try:
                        num = int(code.replace('TNK', ''))
                        existing_numbers.add(num)
                    except ValueError:
                        continue 

                next_number = 1
                while next_number in existing_numbers:
                    next_number += 1
                
                self.tank_code = f"TNK{next_number:03d}"
                
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.tank_code} - {self.item_code}"
    
class TankLayer(models.Model):
    tank_code = models.ForeignKey('TankData' , on_delete = models.CASCADE)
    stock_status = models.ForeignKey('stock.StockStatus' , on_delete = models.CASCADE)
    item_code = models.ForeignKey('TankItem' , on_delete = models.CASCADE)
    vendor = models.ForeignKey('sap_sync.Party' , on_delete = models.CASCADE)
    rate = models.DecimalField(max_digits=10, decimal_places=2)
    quantity_added = models.DecimalField(max_digits=10, decimal_places=2 , null = True)
    quantity_remaining = models.DecimalField(max_digits=10, decimal_places=2 , null = True)
    is_exhausted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True , null = True)
    created_by = models.CharField(max_length=50 , null = True)
    
    class Meta:
        db_table = 'tank_layer'

class TankLog(models.Model):
    
    LOG_TYPE = (
        ("INWARD"  , "INWARD"),
        ("OUTWARD" , "OUTWARD"),
        ("TRANSFER", "TRANSFER"),
    )
    
    log_type = models.CharField(max_length=10 , choices=LOG_TYPE)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    stock_status = models.ForeignKey('stock.StockStatus' , on_delete = models.CASCADE , null = True)
    vehicle_number = models.CharField(max_length=50 , null = True, blank=True)
    rate = models.DecimalField(max_digits=10, decimal_places=2 , null = True)
    party = models.ForeignKey('sap_sync.Party' , on_delete = models.SET_NULL , null = True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.CharField(max_length=50)
    
    class Meta:
        db_table = 'tank_logs'
    

class TankLogConsumption(models.Model):
    """
    For OUTWARD logs only.
    Records which layers were consumed and by how much.
    This is the FIFO cost trail.
    """
    tank_log = models.ForeignKey(
        TankLog, on_delete=models.CASCADE, related_name='consumptions'
    )
    tank_layer = models.ForeignKey(
        TankLayer, on_delete=models.CASCADE, related_name='consumptions'
    )
    quantity_consumed = models.DecimalField(max_digits=10, decimal_places=2)
    rate = models.DecimalField(max_digits=10, decimal_places=2)  # Snapshot from layer at time of consumption
    created_at = models.DateTimeField(auto_now_add=True)
 
    class Meta:
        db_table = 'tank_log_consumption'
 
    def __str__(self):
        return f"Log {self.tank_log.id} | Layer {self.tank_layer.id} | Consumed: {self.quantity_consumed} @ {self.rate}"