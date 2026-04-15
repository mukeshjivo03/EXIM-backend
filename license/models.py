from django.db import models
from django.db.models import Sum
from decimal import Decimal


class AdvanceLicenseHeaders(models.Model):
    STATUS_CHOICES = (
        ('OPEN', 'Open'),
        ('CLOSE', 'Close'),
    )
    
    license_no = models.CharField(max_length = 50 , unique = True , primary_key = True)
    issue_date = models.DateField()
    
    import_validity = models.DateField()
    export_validity = models.DateField()
    
    cif_value_inr = models.DecimalField(max_digits=12, decimal_places = 3)
    cif_value_usd = models.DecimalField(max_digits=12, decimal_places = 3)
    cif_exchange_rate = models.DecimalField(max_digits=8, decimal_places = 3)
    
    fob_value_inr = models.DecimalField(max_digits=12, decimal_places = 3)
    fob_value_usd = models.DecimalField(max_digits=12, decimal_places = 3)
    fob_exhange_rate = models.DecimalField(max_digits=8, decimal_places = 3)
    
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)
    
    
    total_import = models.DecimalField(max_digits=8, decimal_places = 3 , default = 0.00)
    total_export = models.DecimalField(max_digits=8, decimal_places = 3 , default = 0.00)
    to_be_exported = models.DecimalField(max_digits=8, decimal_places = 3, default = 0.00)
    balance = models.DecimalField(max_digits=8, decimal_places = 3 , null = True , blank = True)
    
    def save(self, *args , **kwargs):
        if self.cif_value_inr and self.cif_exchange_rate:
            self.cif_value_usd = self.cif_value_inr / self.cif_exchange_rate
        
        if self.fob_value_inr and self.fob_exhange_rate:
            self.fob_value_usd = self.fob_value_inr / self.fob_exhange_rate

        super().save(*args, **kwargs)
             
    class Meta:
        db_table = 'advance_license_headers'
        
        
class AdvanceLicenseImportLines(models.Model):
    license_no = models.ForeignKey(AdvanceLicenseHeaders, on_delete=models.SET_NULL, null=True, related_name = 'import_lines' , to_field = 'license_no')
    boe_No = models.CharField(max_length = 50)
    boe_value_usd = models.DecimalField(max_digits=12, decimal_places = 3)
    boe_date = models.DateField()
    import_in_mts = models.DecimalField(max_digits=8, decimal_places = 3)
    
    class Meta:
        db_table = 'advance_license_import_lines'
        
    def save(self, *args , **kwargs):
        license =  self.license_no
        super().save(*args, **kwargs)
        
        if license:
            total_import = license.import_lines.aggregate(total_import=Sum('import_in_mts'))['total_import'] or 0
            to_be_exported = Decimal(total_import) - (Decimal(0.031) * Decimal(total_import))
            
            
            license.total_import = total_import
            license.to_be_exported = to_be_exported 
            license.save()
        



class AdvanceLicenseExportLines(models.Model):
    license_no = models.ForeignKey(AdvanceLicenseHeaders, on_delete=models.SET_NULL, null=True, related_name = 'export_lines' , to_field = 'license_no')
    shipping_bill_no = models.CharField(max_length = 50)
    sb_value_usd = models.DecimalField(max_digits=12, decimal_places = 3)
    export_in_mts = models.DecimalField(max_digits=8, decimal_places = 3)
    
    class Meta:
        db_table = 'advance_license_export_lines'

    def save(self, *args, **kwargs):
        license = self.license_no

        if license:
            total_export = license.export_lines.aggregate(
                total_export=Sum('export_in_mts')
            )['total_export'] or Decimal('0')

            # Add current line's value since it's not in DB yet (new record)
            if not self.pk:
                total_export += Decimal(str(self.export_in_mts))

            balance = license.to_be_exported - total_export

            if balance < 0:
                raise ValueError("Total export cannot exceed the to_be_exported quantity.")

            # Validation passed — save line first, then update header
            super().save(*args, **kwargs)

            license.total_export = total_export
            license.balance = balance
            license.save()

        else:
            super().save(*args, **kwargs)  # always save even if no license linked

        

        

class DFIALicenseHeader(models.Model):
    file_no = models.CharField(max_length = 50 , unique = True , primary_key = True)
    issue_date = models.DateField()
    
    export_validity = models.DateField()
    
    fob_value_inr = models.DecimalField(max_digits = 12 , decimal_places = 3)
    fob_value_usd = models.DecimalField(max_digits = 12 , decimal_places = 3)
    fob_exchange_rate = models.DecimalField(max_digits = 8 , decimal_places = 3)
    
    import_validity = models.DateField()
        
    cif_value_inr = models.DecimalField(max_digits = 12, decimal_places = 3)
    cif_value_usd = models.DecimalField(max_digits = 12  , decimal_places = 3)
    cif_exchange_rate = models.DecimalField(max_digits=8 , decimal_places = 3)
    
    status = models.CharField(max_length = 50)
    total_import = models.DecimalField(max_digits=8, decimal_places = 3 , default = 0.00)
    total_export = models.DecimalField(max_digits=8, decimal_places = 3 , default = 0.00)
    
    to_be_imported = models.DecimalField(max_digits=8, decimal_places = 3, default = 0.00)
    balance = models.DecimalField(max_digits=8, decimal_places = 3 , null = True , blank = True)
    
    
    def save(self , *args , **kwargs):
        if self.fob_value_inr and self.fob_exchange_rate:
            self.fob_value_usd = self.fob_value_inr / self.fob_exchange_rate
            
            
        if self.cif_value_inr and self.cif_exchange_rate:
            self.cif_value_usd = self.cif_value_inr / self.cif_exchange_rate
            
       
        super().save(*args , **kwargs)
        
        
    class Meta:
        db_table = 'dfia_license_header'
        
        
class DFIALicenseImportLines(models.Model):
    license_no = models.ForeignKey(DFIALicenseHeader , on_delete = models.SET_NULL , null = True , to_field = 'file_no' , related_name = 'dfia_import_lines')
    boe_no = models.CharField(max_length = 50)
    boe_value_usd = models.DecimalField(max_digits=12, decimal_places = 3)
    boe_date = models.DateField()
    import_in_mts = models.DecimalField(max_digits=8, decimal_places = 3)
    
    class Meta:
        db_table = 'dfia_license_import_lines'
    
    def save(self, *args, **kwargs):
        license = self.license_no
        if license:
            total_import = license.dfia_import_lines.aggregate(
                total_import=Sum('import_in_mts')
            )['total_import'] or Decimal('0')
            
            if not self.pk:
                total_import += Decimal(str(self.import_in_mts))

            balance = license.to_be_imported - total_import

            if balance < 0:
                raise ValueError("Total import cannot exceed the to_be_imported quantity.")

            super().save(*args, **kwargs)

            license.total_import = total_import
            license.balance = balance
            license.save()

        else:
            super().save(*args, **kwargs)

class DFIALicenseExportLines(models.Model):
    license_no = models.ForeignKey(DFIALicenseHeader , on_delete = models.SET_NULL , null = True , to_field = 'file_no' , related_name = 'dfia_export_lines')
    shipping_bill_no = models.CharField(max_length = 50)
    sb_value_usd = models.DecimalField(max_digits=12, decimal_places = 3)
    export_in_mts = models.DecimalField(max_digits=8, decimal_places = 3)
    
    class Meta:
        db_table = 'dfia_license_export_lines'
        
    def save(self, *args, **kwargs):
        license = self.license_no
        super().save(*args, **kwargs)
        if license:
            total_export = license.dfia_export_lines.aggregate(
                total_export=Sum('export_in_mts')
            )['total_export'] or Decimal('0')
            to_be_imported = Decimal(total_export) - (Decimal(0.031) * Decimal(total_export))
            
            license.total_export = total_export
            license.to_be_imported = to_be_imported         
            license.save()
        
    
    
    

        
        

    