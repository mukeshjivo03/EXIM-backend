from django.db import models

# Create your models here.
class syncLogs(models.Model):
    
    SYNC_TYPE = (
        ('PRT' , 'Parties'),
        ('PRD' , 'Product'),
    )

    
    SYNC_STATUS_TYPE = (
        ('STR' , 'STARTED'),
        ('FLD' , 'FAILED'),
        ('SCS' , 'SUCCESS')    
    )
    
    
    sync_type = models.CharField(choices=SYNC_TYPE , max_length=3)
    status = models.CharField(choices=SYNC_STATUS_TYPE , max_length=3)
    triggered_by = models.CharField(max_length=50 , default='Manual')
    started_at = models.DateTimeField(blank=True , null=True)
    completed_at = models.DateTimeField(blank=True , null=True)
    error_message = models.TextField(blank=True , null=True)
    records_procesed = models.IntegerField(default=0)
    records_created= models.IntegerField(default=0)
    records_updated = models.IntegerField(default=0)
 
    class Meta:
        db_table = 'sync_log'   
    
    

class RMProducts(models.Model):

    item_code = models.CharField(max_length=50, unique=True) 
    item_name = models.CharField(max_length=255, null=True, blank=True)
    category = models.CharField(max_length=50, null=True, blank=True)
    sal_factor2 = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    u_tax_rate = models.IntegerField(null=True, blank=True)
    deleted = models.CharField(max_length=1, null=True, blank=True)
    u_variety = models.CharField(max_length=50, null=True, blank=True)
    sal_pack_un = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    u_brand = models.CharField(max_length=50, null=True, blank=True)
    u_unit = models.CharField(max_length=50, null=True, blank=True)
    u_sub_group = models.CharField(max_length=50, null=True, blank=True)
    
    class Meta:
        db_table = 'rm_goods'
        

class FGProducts(models.Model):

    item_code = models.CharField(max_length=50, unique=True) 
    item_name = models.CharField(max_length=255, null=True, blank=True)
    category = models.CharField(max_length=50, null=True, blank=True)
    sal_factor2 = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    u_tax_rate = models.IntegerField(null=True, blank=True)
    deleted = models.CharField(max_length=1, null=True, blank=True)
    u_variety = models.CharField(max_length=50, null=True, blank=True)
    sal_pack_un = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    u_brand = models.CharField(max_length=50, null=True, blank=True)
    u_unit = models.CharField(max_length=50, null=True, blank=True)
    u_sub_group = models.CharField(max_length=50, null=True, blank=True)
    
    class Meta:
        db_table = 'fg_goods'



class Party(models.Model):
    card_code = models.CharField(max_length=50, unique=True) 
    card_name = models.CharField(max_length=50, null=True, blank=True)
    state = models.CharField(max_length=5, null=True, blank=True)
    u_main_group = models.CharField(max_length=50, null=True, blank=True)
    country = models.CharField(max_length=5, null=True, blank=True)
    
    class Meta:
        db_table = 'Party'