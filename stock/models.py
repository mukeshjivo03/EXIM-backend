from django.db import models
from sap_sync.models import RMProducts , Party 
from tank.models import TankData , TankItem , TankLog

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
    
    REMAINDER_ACTION_CHOICES = (
        ('RETAIN',    'Retain — reduce parent, keep alive'),
        ('TOLERATE',  'Tolerate — absorb difference, close source'),
        ('DEBIT',     'Debit — log as loss, close source'),
    )

    STORAGE_STATUSES = frozenset([
        'AT_REFINERY',
        'KANDLA_STORAGE',
        'MUNDRA_PORT',
        'IN_TANK',
        'OUT_SIDE_FACTORY',
    ])
    
    item_code = models.ForeignKey(TankItem, on_delete=models.SET_NULL, null=True ,to_field = 'tank_item_code')
    status = models.CharField(max_length=50 , choices=STATUS_CHOICES)
    vendor_code = models.ForeignKey(Party, on_delete=models.SET_NULL , null = True , to_field = 'card_code')
    rate = models.DecimalField(max_digits=10, decimal_places=3)
    rate_in_litres = models.DecimalField(max_digits=10, decimal_places=3 , null = True , blank = True)
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
    
    parent = models.ForeignKey('self',null=True, blank=True,on_delete=models.SET_NULL,related_name='children',)
    is_accumulator = models.BooleanField(default=False)
    remainder_action = models.CharField(max_length=20,choices=REMAINDER_ACTION_CHOICES,null=True, blank=True)
    job_work = models.CharField(max_length=50 , blank=True , null= True)

    class Meta:
        db_table = 'stock_status'
        
    def __str__(self):
        return f"{self.item_code} - {self.status}"
    
    @property
    def can_be_parent(self) -> bool:
        return self.status in self.STORAGE_STATUSES
    
    
    def save(self ,*args , **kwargs):

        if self.status == 'AT_REFINERY' and self.item_code_id == 'RM0CDRO':
            self.quantity = self.quantity - (Decimal('0.03') * self.quantity)
            self.item_code_id = 'RM00C01'
        if self.rate is not None:
            self.rate_in_litres = self.rate / Decimal(1.09089)
            
        if self.rate is not None and self.quantity is not None:
            self.total = self.rate * self.quantity
        else:
            self.total = Decimal('0.00')

        if self.quantity is not None:
            self.quantity_in_litre = self.quantity * Decimal('1.0989')
        else:
            self.quantity_in_litre = Decimal('0.00')
            
        is_new = self.pk is None

        if not is_new:
            old_instance = StockStatus.objects.get(pk=self.pk)
            track_fields = ['status' , 'rate' ,'quantity']

            for field in track_fields:
                old_val = getattr(old_instance, field)
                new_val = getattr(self, field)
                
                if field == "status" and new_val == "IN_TANK":
                    
                    TankLog.objects.create(
                        log_type = 'INWARD',
                        quantity = self.quantity,
                        stock_status = self,
                        vehicle_number = self.vehicle_number,
                        rate = self.rate,
                        party=self.vendor_code.card_name if self.vendor_code else None,
                        created_by = self.created_by
                    )
                    
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
            if is_new and self.status == 'IN_TANK':
                    TankLog.objects.create(
                        log_type = 'INWARD',
                        quantity = self.quantity,
                        stock_status = self,
                        vehicle_number = self.vehicle_number,
                        rate = self.rate,
                        party=self.vendor_code.card_name if self.vendor_code else None,
                        created_by = self.created_by
                    )
                                    
            StockStatusUpdateLog.objects.create(
                stock_id = self,
                field_name = 'All',
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
        
    


class DebitEntry(models.Model):
    stock = models.ForeignKey(StockStatus, on_delete=models.SET_NULL, null=True, related_name='debits')
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    rate = models.DecimalField(max_digits=10, decimal_places=2)
    total = models.DecimalField(max_digits=20, decimal_places=2, editable=False)
    responsible_party = models.ForeignKey(Party, on_delete=models.SET_NULL, null=True, to_field='card_code')
    reason = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.CharField(max_length=50)

    class Meta:
        db_table = 'stock_debit_entries'

    def save(self, *args, **kwargs):
        self.total = self.quantity * self.rate
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Debit {self.quantity} MTS @ {self.rate} — {self.stock}"