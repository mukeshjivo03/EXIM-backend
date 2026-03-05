from django.db import models

# Create your models here.
class syncLogs(models.Model):
    
    SYNC_TYPE = (
        ('PRT' , 'Parties'),
        ('PRD' , 'Products'),
        ('DMC', 'Domestic_Contracts')
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
    total_trans_value = models.DecimalField(max_digits=18, decimal_places=6, null=True, blank=True)
    total_in_qty = models.DecimalField(max_digits=18, decimal_places=6, null=True, blank=True)
    total_out_qty = models.DecimalField(max_digits=18, decimal_places=6, null=True, blank=True)
    total_qty = models.DecimalField(max_digits=18, decimal_places=6, null=True, blank=True)
    rate = models.DecimalField(max_digits=18, decimal_places=6, null=True, blank=True)

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
        
class DomesticContracts(models.Model):
    po_number = models.CharField(max_length=50) 
    po_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=5, null=True, blank=True)
    product_code = models.CharField(max_length=50, null=True, blank=True)
    product_name = models.CharField(max_length=255, null=True, blank=True)
    vendor = models.CharField(max_length=255, null=True, blank=True)
    contract_qty = models.DecimalField(max_digits=15, decimal_places=4, null=True, blank=True)
    contract_rate = models.DecimalField(max_digits=15, decimal_places=4, null=True, blank=True)
    contract_value = models.DecimalField(max_digits=15, decimal_places=4, null=True, blank=True)
    load_qty = models.DecimalField(max_digits=15, decimal_places=4, null=True, blank=True) 
    unload_qty = models.CharField(max_length=5, null=True, blank=True)  
    allowance = models.DecimalField(max_digits=15, decimal_places=4, null=True, blank=True)
    transporter = models.CharField(max_length=255, null=True, blank=True)
    vehicle_no = models.CharField(max_length=30, null=True, blank=True)
    bilty_no = models.CharField(max_length=30, null=True, blank=True)
    bilty_date = models.DateField(null=True, blank=True)
    grpo_no = models.CharField(max_length=30, null=True, blank=True)
    grpo_date = models.DateField(null=True, blank=True)
    invoice_no = models.CharField(max_length=30, null=True, blank=True)
    basic_amount = models.DecimalField(max_digits=15, decimal_places=4, null=True, blank=True)
    landed_cost = models.DecimalField(max_digits=15, decimal_places=4, null=True, blank=True)
    net_amount = models.DecimalField(max_digits=15, decimal_places=4, null=True, blank=True)

    
    
    
    class Meta:
        db_table = 'domestic_contracts'
        unique_together = ('po_number', 'grpo_no')
    
    
    
    

    
    