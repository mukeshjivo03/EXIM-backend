from django.db import models
from django.utils import timezone 
from datetime import datetime
import uuid
from django.conf import settings
from decimal import Decimal



from sap_sync.models import RMProducts , Party 
from tank.models import TankData , TankItem , TankLog


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
        'IN_CONTRACT',
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
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    total = models.DecimalField(max_digits=20, decimal_places=2 , editable = False , default = '0.00')

    rate_in_litres = models.DecimalField(max_digits=10, decimal_places=3 , null = True , blank = True)
    quantity_in_litre = models.DecimalField(max_digits=10, decimal_places=2 , default=Decimal('0.00'))
    job_work = models.CharField(max_length=50 , blank=True , null= True)

    vehicle_number = models.CharField(max_length=50 , null = True, blank=True)
    transporter = models.CharField(max_length=255 , null = True, blank=True)
    location = models.CharField(max_length=255  , null = True, blank=True)
    eta = models.DateField(blank=True, null=True)

    parent = models.ForeignKey('self',null=True, blank=True,on_delete=models.SET_NULL,related_name='children',)
    is_accumulator = models.BooleanField(default=False)
    arrival_date = models.DateField(null=True, blank=True)
    remainder_action = models.CharField(max_length=20,choices=REMAINDER_ACTION_CHOICES,null=True, blank=True)


    # BOE Fields 
    # boe_number = models.CharField(max_length=100 , null = True, blank=True)
    # boe_date = models.DateField(null=True, blank=True)
    # net_weight = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    # gross_weight = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    # invoice_number = models.CharField(max_length=100, null=True, blank=True)
    # usd_price = models.DecimalField(max_digits=20, decimal_places=4, null=True, blank=True)
    
    
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.CharField(max_length=50)
    deleted = models.BooleanField(default=False)
    

    class Meta:
        db_table = 'stock_status'
        permissions = [('view_vehicle_report' , 'Can view Vehicle Report')]
    
    def save(self, *args, **kwargs):
        # ── existing RM0CDRO swap logic ──────────────────────────────────────
        if self.item_code.tank_item_code == 'RM0CDRO' and self.status == 'AT_REFINERY' and self.quantity is not None:
            self.item_code = TankItem.objects.get(tank_item_code='RM00C01')
            deduction_qty = Decimal('0.03') * self.quantity
            self.quantity = self.quantity - deduction_qty



            
        # ── density conversions ──────────────────────────────────────────────
        if self.quantity and self.rate and self.item_code:
            density = Decimal('1.0989')
            self.quantity_in_litre = (self.quantity * density).quantize(Decimal('0.01'))
            self.rate_in_litres    = (self.rate / density).quantize(Decimal('0.001'))
            
        if self.quantity <= Decimal('0.00'):
            self.deleted = True
            


        # ── capture pre-save state ───────────────────────────────────────────
        is_new = self.pk is None
        old_status = None
        old_quantity = None

        if not is_new:
            try:
                prev = StockStatus.objects.only('status', 'quantity', 'eta').get(pk=self.pk)
                old_status = prev.status
                old_quantity = prev.quantity
                old_eta = prev.eta  # capture previous eta
            except StockStatus.DoesNotExist:
                pass

        # Set arrival_date to the previously stored eta when it reaches the factory
       
        if not is_new:
            
            if not is_new and old_status != 'OUT_SIDE_FACTORY' and self.status == 'OUT_SIDE_FACTORY':
                self.arrival_date = old_eta
            
            
            
            try:
                prev = StockStatus.objects.only('status', 'quantity').get(pk=self.pk)
                old_status = prev.status
                old_quantity = prev.quantity
            except StockStatus.DoesNotExist:
                pass

        super().save(*args, **kwargs)

        # ── DebitEntry on → IN_TANK transition ───────────────────────────────
        if (
            not is_new
            and old_status != 'IN_TANK'
            and self.status == 'IN_TANK'
            and old_quantity is not None
            and old_quantity != self.quantity       # only if there's an actual loss
        ):
            diff = old_quantity - self.quantity
            if diff != Decimal('0.00'):
                if diff > 0:
                    type = 'LOSS'
                    reason = f"Quantity loss on IN_TANK transition (was {old_quantity}, now {self.quantity})"
                else:
                    type = 'GAIN'
                    reason = f"Quantity gain on IN_TANK transition (was {old_quantity}, now {self.quantity})"

                DebitEntry.objects.create(
                    stock=self,
                    quantity=diff,
                    rate=self.rate,
                    type=type,
                    responsible_party=self.vendor_code,
                    vehicle_number=self.vehicle_number,
                    responsible_transporter=self.transporter,
                    reason=reason,
                    
                    created_by=self.created_by,
                )

                TankLog.objects.create(
                    log_type='INWARD',
                    quantity=self.quantity,
                    stock_status=self,
                    vehicle_number=self.vehicle_number,
                    item = self.item_code.tank_item_code,
                    rate=self.rate,
                    arrival = self.eta,
                    party=self.vendor_code.card_name if self.vendor_code else None,
                    created_by = self.created_by
                )

    
    def __str__(self):
        return f"{self.item_code} - {self.status}"
    
    @property
    def can_be_parent(self) -> bool:
        return self.status in self.STORAGE_STATUSES
    
    



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
    TYPE_CHOICES = (
        ('LOSS', 'Loss'),
        ('GAIN', 'Gain'),
    )
    
    stock = models.ForeignKey(StockStatus, on_delete=models.SET_NULL, null=True, related_name='debits')
    type = models.CharField(max_length=10, choices=TYPE_CHOICES, editable=False)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    rate = models.DecimalField(max_digits=10, decimal_places=2)
    total = models.DecimalField(max_digits=20, decimal_places=2, editable=False)
    responsible_party = models.ForeignKey(Party, on_delete=models.SET_NULL, null=True, to_field='card_code')
    vehicle_number = models.CharField(max_length=50, null=True, blank=True)
    responsible_transporter = models.CharField(max_length=255, null=True, blank=True)  # denormalized fallback
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
    

class StockStatusChangeSession(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    stock = models.ForeignKey(StockStatus, on_delete=models.CASCADE, related_name='change_sessions')
    action = models.CharField(max_length=10, choices=[('CREATE', 'Create'), ('UPDATE', 'Update')])
    changed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    changed_by_label = models.CharField(max_length=100)  # denormalized fallback
    timestamp = models.DateTimeField(auto_now_add=True)
    note = models.CharField(max_length=255, blank=True)  # optional reason/context

    class Meta:
        db_table = 'stock_change_sessions'
        ordering = ['-timestamp']


class StockStatusFieldLog(models.Model):
    session = models.ForeignKey(StockStatusChangeSession, on_delete=models.CASCADE, related_name='field_logs')
    field_name = models.CharField(max_length=100)
    old_value = models.JSONField(null=True)   # preserves type: Decimal → str in JSON is fine
    new_value = models.JSONField(null=True)

    class Meta:
        db_table = 'stock_field_logs'