from django.db import models
from sap_sync.models import RMProducts , Party 


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
        ('PROCESSING' , 'PROCESSING')
    )
    
    item_code = models.ForeignKey(RMProducts, on_delete=models.CASCADE)
    status = models.CharField(max_length=50 , choices=STATUS_CHOICES)
    vendor_code = models.ForeignKey(Party, on_delete=models.CASCADE)
    rate = models.DecimalField(max_digits=10, decimal_places=2)
    total = models.DecimalField(max_digits=12, decimal_places=2)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.CharField(max_length=50)
    deleted = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'stock_status'
        
    def __str__(self):
        return f"{self.item_code} - {self.status}"
    
    def save(self ,*args , **kwargs):
        if self.pk:
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



class StockStatusUpdateLog(models.Model):
    stock_id = models.ForeignKey(StockStatus , on_delete=models.PROTECT)
    field_name = models.CharField(max_length=30)   
    old_value = models.CharField(max_length=30)
    new_value = models.CharField(max_length=30)
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.CharField(max_length=30)
    
    class Meta:
        db_table = 'stock_update_logs'