from decimal import Decimal

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


class DomesticContractDetails(models.Model):
    """One row of the DC workbook — a single invoice / vehicle movement against a PO.

    Keyed on invoice_no: a PO can carry many loads, and the GRPO number is blank
    on most rows, so po_number + grpo_no is not unique in this sheet.
    Amount / rate columns are recomputed on import, never trusted from the file.
    """

    SHORTAGE_ALLOWANCE_PCT = Decimal('0.0025')   # 0.25% of load qty

    STATUS_CHOICES = (
        ("RECEIVED", "RECEIVED"),
        ("IN_TRANSIT", "IN_TRANSIT"),
        ("PENDING", "PENDING"),
    )

    DEL_TERMS_CHOICES = (
        ("FOR", "FOR"),
        ("EXW", "EXW"),
    )

    # ----------------------------------IDENTITY------------------------------------------
    invoice_no = models.CharField(max_length=50, unique=True)
    invoice_date = models.DateField(null=True, blank=True)
    po_number = models.CharField(max_length=50, db_index=True)
    grpo_no = models.CharField(max_length=30, null=True, blank=True, db_index=True)
    grpo_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, null=True, blank=True)

    # ----------------------------------PARTY / PRODUCT------------------------------------------
    supplier = models.CharField(max_length=255)
    item = models.CharField(max_length=255)
    del_terms = models.CharField(max_length=10, choices=DEL_TERMS_CHOICES, null=True, blank=True)
    contract_qty = models.DecimalField(max_digits=15, decimal_places=4, null=True, blank=True)

    # ----------------------------------LOADING------------------------------------------
    load_qty_mts = models.DecimalField(max_digits=15, decimal_places=4, null=True, blank=True)
    inv_rate = models.DecimalField(max_digits=15, decimal_places=4, null=True, blank=True)
    basic_amount = models.DecimalField(max_digits=18, decimal_places=4, null=True, blank=True)
    # basic_amount = load_qty_mts * inv_rate

    # ----------------------------------UNLOADING------------------------------------------
    unload_qty_mts = models.DecimalField(max_digits=15, decimal_places=4, null=True, blank=True)
    unload_qty_ltr = models.DecimalField(max_digits=18, decimal_places=4, null=True, blank=True)
    rate_in_sap_unloading = models.DecimalField(max_digits=18, decimal_places=6, null=True, blank=True)
    # rate_in_sap_unloading = basic_amount / unload_qty_mts

    # ----------------------------------SHORTAGE------------------------------------------
    shortage_recd_mts = models.DecimalField(max_digits=15, decimal_places=6, null=True, blank=True)
    # shortage_recd_mts = load_qty_mts - unload_qty_mts
    allow_shortage_mts = models.DecimalField(max_digits=15, decimal_places=6, null=True, blank=True)
    # allow_shortage_mts = load_qty_mts * 0.25%
    deduction_qty_mts = models.DecimalField(max_digits=15, decimal_places=6, null=True, blank=True)
    # deduction_qty_mts = shortage_recd_mts - allow_shortage_mts (kept signed; negative = within allowance)
    deduct_amount = models.DecimalField(max_digits=18, decimal_places=4, null=True, blank=True)
    # deduct_amount = max(deduction_qty_mts, 0) * inv_rate

    # ----------------------------------FREIGHT / BROKERAGE------------------------------------------
    freight_rate = models.DecimalField(max_digits=15, decimal_places=4, null=True, blank=True)
    freight_amount = models.DecimalField(max_digits=18, decimal_places=4, null=True, blank=True)
    # freight_amount = freight_rate * unload_qty_mts
    brokerage_rate = models.DecimalField(max_digits=15, decimal_places=4, null=True, blank=True)
    brokerage_amount = models.DecimalField(max_digits=18, decimal_places=4, null=True, blank=True)
    # brokerage_amount = brokerage_rate * load_qty_mts
    bilty_charges = models.DecimalField(max_digits=15, decimal_places=4, null=True, blank=True)
    # bilty_charges are recorded but excluded from landed cost, matching the workbook

    # ----------------------------------LANDED COST------------------------------------------
    cost_per_mt = models.DecimalField(max_digits=18, decimal_places=6, null=True, blank=True)
    # cost_per_mt = (basic_amount + freight_amount + brokerage_amount) / unload_qty_mts
    cost_per_kl = models.DecimalField(max_digits=18, decimal_places=6, null=True, blank=True)
    # cost_per_kl = cost_per_mt * unload_qty_mts / unload_qty_ltr * 1000
    cost_per_ltr = models.DecimalField(max_digits=18, decimal_places=6, null=True, blank=True)
    # cost_per_ltr = cost_per_kl / 1000

    # ----------------------------------LOGISTICS------------------------------------------
    transporter_name = models.CharField(max_length=255, null=True, blank=True)
    vehicle_number = models.CharField(max_length=30, null=True, blank=True)
    bilty_number = models.CharField(max_length=30, null=True, blank=True)

    # ----------------------------------META------------------------------------------
    source_file = models.CharField(max_length=255, null=True, blank=True)
    source_row = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'domestic_contract_details'
        ordering = ['-invoice_date', 'invoice_no']
        indexes = [
            models.Index(fields=['supplier']),
            models.Index(fields=['item']),
            models.Index(fields=['invoice_date']),
        ]

    def __str__(self):
        return f"{self.invoice_no} | {self.po_number} | {self.item}"

    def recalculate(self):
        """Derive every computed column from the raw inputs. Returns self."""
        load = self.load_qty_mts
        unload = self.unload_qty_mts
        rate = self.inv_rate

        self.basic_amount = load * rate if load is not None and rate is not None else None

        if load is not None and unload is not None:
            self.shortage_recd_mts = load - unload
            self.allow_shortage_mts = load * self.SHORTAGE_ALLOWANCE_PCT
            self.deduction_qty_mts = self.shortage_recd_mts - self.allow_shortage_mts
            if rate is not None:
                self.deduct_amount = max(self.deduction_qty_mts, Decimal('0')) * rate

        if self.basic_amount is not None and unload:
            self.rate_in_sap_unloading = self.basic_amount / unload

        if self.freight_rate is not None and unload is not None:
            self.freight_amount = self.freight_rate * unload
        if self.brokerage_rate is not None and load is not None:
            self.brokerage_amount = self.brokerage_rate * load

        if self.basic_amount is not None and unload:
            total = self.basic_amount + (self.freight_amount or 0) + (self.brokerage_amount or 0)
            self.cost_per_mt = total / unload
            if self.unload_qty_ltr:
                self.cost_per_kl = self.cost_per_mt * unload / self.unload_qty_ltr * 1000
                self.cost_per_ltr = self.cost_per_kl / 1000

        return self
