from django.db import models
from sap_sync.models import RMProducts , Party 
from tank.models import TankData , TankItem
from decimal import Decimal

class StockStatus(models.Model):
    STATUS_CHOICES = (
        ('OUT_SIDE_FACTORY' , 'OUT_SIDE_FACTORY'),
        ('ON_THE_WAY' , 'ON_THE_WAY'),
        ('UNDER_LOADING' , 'UNDER_LOADING'),
        ('AT_REFINERY' , 'AT_REFINERY'),
        ('OTW_TO_REFINERY' , 'OTW_TO_REFINERY'),
        ('KANDLA_STORAGE' , 'KANDLA_STORAGE'),
        ('MUNDRA_PORT' , 'MUNDRA_PORT'),
        ('ON_THE_SEA' , 'ON_THE_SEA'),
        ('IN_CONTRACT' , 'IN_CONTRACT'),
        ('COMPLETED'  , 'COMPLETED'),
        ('DELIVERED' , 'DELIVERED'),
        ('IN_TRANSIT' , 'IN_TRANSIT'),
        ('PENDING' ,  'PENDING'),
        ('PROCESSING' , 'PROCESSING'),
        ('IN_TANK' , 'IN_TANK')
    )
    
    item_code = models.ForeignKey(TankItem, on_delete=models.SET_NULL, null=True ,to_field = 'tank_item_code')
    status = models.CharField(max_length=50 , choices=STATUS_CHOICES)
    vendor_code = models.ForeignKey(Party, on_delete=models.SET_NULL , null = True , to_field = 'card_code')
    rate = models.DecimalField(max_digits=10, decimal_places=2)
    total = models.DecimalField(max_digits=20, decimal_places=2 , editable = False , default = '0.00')
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    quantity_in_litre = models.DecimalField(max_digits=10, decimal_places=2 , default=Decimal('0.00'))
    vehicle_number = models.CharField(max_length=50 , null = True, blank=True)
    transporter = models.CharField(max_length=255 , null = True, blank=True)
    location = models.CharField(max_length=255  , null = True, blank=True)
    eta = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.CharField(max_length=50)
    deleted = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'stock_status'
        
    def __str__(self):
        return f"{self.item_code} - {self.status}"
    
    def save(self ,*args , **kwargs):

        if self.rate is not None and self.quantity is not None:
            self.total = self.rate * self.quantity
        else:
            self.total = Decimal('0.00')
            
        if self.quantity is not None:
            self.quantity_in_litre = self.quantity / Decimal('0.91')
        else:
            self.quantity_in_litre = Decimal('0.00')
            
            
        is_new = self.pk is None

        if not is_new:
            old_instance = StockStatus.objects.get(pk=self.pk)
            track_fields = ['status' , 'rate' ,'quantity']

            for field in track_fields:
                old_val = getattr(old_instance, field)
                new_val = getattr(self, field)

                if old_val != new_val:
                    StockStatusUpdateLog.objects.create(
                        stock_id = self,
                        field_name = field,
                        old_value = old_val,
                        new_value = new_val,
                        updated_by = self.created_by,
                    )

        super().save(*args, **kwargs)

        if is_new:
            StockStatusUpdateLog.objects.create(
                stock_id = self,
                field_name = 'CREATED',
                old_value = '',
                new_value = f"qty={self.quantity}, rate={self.rate}, status={self.status}",
                updated_by = self.created_by,
            )



class StockStatusUpdateLog(models.Model):
    stock_id = models.ForeignKey(StockStatus , on_delete=models.SET_NULL , null = True)
    field_name = models.CharField(max_length=50)
    old_value = models.CharField(max_length=255)
    new_value = models.CharField(max_length=255)
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.CharField(max_length=50)
    
    class Meta:
        db_table = 'stock_update_logs'
        
    
