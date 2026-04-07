from django.db import models


class DomesticReports(models.Model):

    STATUS_CHOICES = (
        ("CONTRACT" , "CONTRACT"),
        ("PO" , "PO"),
        ("MAIL_APPROVAL" , "MAIL_APPROVAL"),
        ("PAYMENT" , "PAYMENT"),
        ("TPT/LOADING" , "TPT/LOADING"),
        ("IN_TRANSIT" , "IN_TRANSIT"),
        ("FACTORY" , "FACTORY"),
        ("RECIEVED" , "RECIEVED"),
    )
    
    # ----------------------------------FORM 1------------------------------------------
    status = models.CharField(max_length=50 , choices=STATUS_CHOICES)
    product_code= models.CharField(max_length=20)
    vendor_code = models.CharField(max_length=50)
    po_number = models.CharField(max_length=50)
    po_date = models.DateField()

    contract_qty = models.DecimalField(max_digits=15, decimal_places=2 , null=True , blank=True)
    contract_rate = models.DecimalField(max_digits=15, decimal_places=2, null=True , blank=True)
    contract_total = models.DecimalField(max_digits = 15 , decimal_places = 2 , null=True , blank = True )
    # show total = contract qty * contract rate

    
    # ----------------------------------FORM 2------------------------------------------
    load_qty = models.DecimalField(max_digits=15, decimal_places=2, null=True , blank=True)
    basic_amount = models.DecimalField(max_digits=15, decimal_places=2, null=True , blank=True)
    # basic_amount = load qty * load rate 
    

    unload_qty = models.DecimalField(max_digits=15, decimal_places=2, null=True , blank=True)
    shortage = models.DecimalField(max_digits=15, decimal_places=2, null=True , blank=True)
    
    allow_shortage = models.DecimalField(max_digits=15, decimal_places=2, null=True , blank=True)
    # allow_shortage  - 0.25 * load_qty 

    deduction_qty = models.DecimalField(max_digits=15, decimal_places=2, null=True , blank=True)
    # deductionQty = (shortage)rec_shortage - allow_shortage

    deduction_amount = models.DecimalField(max_digits=15, decimal_places=2, null=True , blank=True)
    # deduction_amount = ( deductionQty / 1000) * loadrate
    # if deduction < 0 then deduction qty = 0 deduction amount = 0
    # else warning 


    # ----------------------------------FORM 3------------------------------------------
    transporter_code = models.CharField(max_length=50, null=True , blank=True)
    transporter_name = models.CharField(max_length=200, null=True , blank=True)
    
    bility_number = models.CharField(max_length=50, null=True , blank=True)
    bility_date = models.DateField(null=True , blank=True)
    
    frieght_rate = models.DecimalField(max_digits=15, decimal_places=2, null=True , blank=True)
    freight_amount = models.DecimalField(max_digits=15, decimal_places=2, null=True , blank=True)

    grpo_date = models.DateField( null=True , blank=True)
    grpo_number = models.CharField(max_length=50, null=True , blank=True)
    
    brokerage_amount = models.DecimalField(max_digits=15, decimal_places=2 ,null=True , blank=True)
    vehicle_number = models.CharField(max_length=50, null=True , blank=True)
    invoice_number= models.CharField(max_length=50, null=True , blank=True)

    # Freight  rate = unload qty * freight rate 
    

    # ----------------------------------Meta Data------------------------------------------
    created_by = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    deleted = models.IntegerField(default=0)
    Completed =models.IntegerField(default=0)
    

    class Meta:
        db_table = 'contracts'

        
    