from django.db import models

class AdvanceLicenseHeaders(models.Model):
    STATUS_CHOICES = (
        ('OPEN', 'Open'),
        ('CLOSE', 'Close'),
    )
    
    license_no = models.CharField(max_length = 50 , unique = True , primary_key = True)
    issue_date = models.DateField()
    import_validity = models.DateField()
    export_validity = models.DateField()
    import_in_mts = models.DecimalField(max_digits=8, decimal_places = 3)
    cif_value_inr = models.DecimalField(max_digits=12, decimal_places = 3)
    cif_value_usd = models.DecimalField(max_digits=12, decimal_places = 3)
    cif_exchange_rate = models.DecimalField(max_digits=8, decimal_places = 3)
    
    export_in_mts = models.DecimalField(max_digits=8, decimal_places = 3)
    
    fob_value_inr = models.DecimalField(max_digits=12, decimal_places = 3)
    fob_value_usd = models.DecimalField(max_digits=12, decimal_places = 3)
    fob_exhange_rate = models.DecimalField(max_digits=8, decimal_places = 3)
    
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)

    def save(self, *args , **kwargs):
        if self.cif_value_inr and self.cif_exchange_rate:
            self.cif_value_usd = self.cif_value_inr / self.cif_exchange_rate
            
        
        if self.fob_value_inr and self.fob_exhange_rate:
            self.fob_value_usd = self.fob_value_inr / self.fob_exhange_rate

        super().save(*args, **kwargs)
             
        
        
    class Meta:
        db_table = 'advance_license_headers'
        
        
class AdvanceLicenseLines(models.Model):
    license_no = models.ForeignKey(AdvanceLicenseHeaders, on_delete=models.SET_NULL, null=True, related_name = 'lincense_lines' , to_field = 'license_no')
    boe_No = models.CharField(max_length = 50)
    boe_value_usd = models.DecimalField(max_digits=12, decimal_places = 3)
    shipping_bill_no = models.CharField(max_length = 50)
    date = models.DateField()
    sb_value_usd = models.DecimalField(max_digits=12, decimal_places = 3)
    import_in_mts = models.DecimalField(max_digits=8, decimal_places = 3)
    export_in_mts = models.DecimalField(max_digits=8, decimal_places = 3)
    balance = models.DecimalField(max_digits=12, decimal_places = 3)
    
    class Meta:
        db_table = 'advance_license_lines'
        

        

class DFIALicenseHeader(models.Model):
    file_no = models.CharField(max_length = 50 , unique = True , primary_key = True)
    issue_date = models.DateField()
    
    export_validity = models.DateField()
    export_in_mts = models.DecimalField(max_digits=8 , decimal_places = 3)
    
    fob_value_inr = models.DecimalField(max_digits = 12 , decimal_places = 3)
    fob_value_usd = models.DecimalField(max_digits = 12 , decimal_places = 3)
    fob_exchange_rate = models.DecimalField(max_digits = 8 , decimal_places = 3)
    
    import_validity = models.DateField()
    import_in_mts = models.DecimalField(max_digits = 12 , decimal_places = 3)
    
    cif_value_inr = models.DecimalField(max_digits = 12, decimal_places = 3)
    cif_value_usd = models.DecimalField(max_digits = 12  , decimal_places = 3)
    cif_exchange_rate = models.DecimalField(max_digits=8 , decimal_places = 3)
    
    status = models.CharField(max_length = 50)
    
    def save(self , *args , **kwargs):
        if self.fob_value_inr and self.fob_exchange_rate:
            self.fob_value_usd = self.fob_value_inr / self.fob_exchange_rate
            
        elif self.fob_value_usd and self.fob_exchange_rate:
            self.fob_value_inr = self.fob_value_usd * self.fob_exchange_rate
            
            
        if self.cif_value_inr and self.cif_exchange_rate:
            self.cif_value_usd = self.cif_value_inr / self.cif_exchange_rate
            
        elif self.cif_value_usd and self.cif_exchange_rate:
            self.cif_value_inr = self.cif_value_usd * self.cif_exchange_rate
            
       
        super().save(*args , **kwargs)
        
        
    class Meta:
        db_table = 'dfia_license_header'
        
        
class DFIALicenseLines(models.Model):
    license_no = models.ForeignKey(DFIALicenseHeader , on_delete = models.SET_NULL , null = True , to_field = 'file_no' , related_name = 'dfia_license_lines')
    boe_no = models.CharField(max_length = 50)
    shipping_bill_no = models.CharField(max_length = 50)
    date = models.DateField()
    to_be_imported_in_mts = models.DecimalField(max_digits = 8 , decimal_places = 3)
    exported_in_mts = models.DecimalField(max_digits = 8 , decimal_places = 3)
    balance = models.DecimalField(max_digits = 8 , decimal_places = 3)
    sb_value_inr = models.DecimalField(max_digits = 15 , decimal_places = 3)
    
    
    class Meta:
        db_table = 'dfia_license_lines'
        
        
    
    
    
    

        
        

    