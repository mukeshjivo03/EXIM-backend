from django.db import models


class DomesticReports(models.Model):
    status = models.CharField(max_length=50)
    product_code= models.CharField(max_length=20)
    vendor_code = models.CharField(max_length=50)
    po_number = models.CharField(max_length=50)
    po_date = models.DateField()
    contract_qty = models.DecimalField(max_digits=15, decimal_places=2)
    contract_rate = models.DecimalField(max_digits=15, decimal_places=2)
    load_qty = models.DecimalField(max_digits=15, decimal_places=2)
    basic_amount = models.DecimalField(max_digits=15, decimal_places=2)
    unload_qty = models.DecimalField(max_digits=15, decimal_places=2)
    shortage_rec = models.DecimalField(max_digits=15, decimal_places=2)
    allow_shortage = models.DecimalField(max_digits=15, decimal_places=2)
    deduction = models.DecimalField(max_digits=15, decimal_places=2)
    deduct_amount = models.DecimalField(max_digits=15, decimal_places=2)
    transporter_code = models.CharField(max_length=50)
    transporter_name = models.CharField(max_length=200)
    bility_number = models.CharField(max_length=50)
    bility_date = models.DateField()
    frieght_rate = models.DecimalField(max_digits=15, decimal_places=2)
    freight_amount = models.DecimalField(max_digits=15, decimal_places=2)
    grpo_date = models.DateField()
    grpo_number = models.CharField(max_length=50)
    brokerage_amount = models.DecimalField(max_digits=15, decimal_places=2)
    brokerage_rate = models.DecimalField(max_digits=15, decimal_places=2)
    vehicle_number = models.CharField(max_length=50)
    invoice_number= models.CharField(max_length=50)
    created_by = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    deleted = models.IntegerField(default=0)
    Completed =models.IntegerField(default=0)
    

    class Meta:
        db_table = 'old_domestic_contract'
        
    