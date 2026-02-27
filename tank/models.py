from django.db import models
from django.db import models, transaction

# Create your models here.
class TankItem(models.Model):
    tank_item_code = models.CharField(unique=True ,max_length=50 , primary_key = True)
    tank_item_name = models.CharField(max_length = 255)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.CharField(max_length=50)
    color = models.CharField(max_length=10)
    
    class Meta:
        db_table = 'tank_item'
        
    def __str__(self):
        return self.tank_item_name
    

class TankData(models.Model):

    tank_code = models.CharField(primary_key=True, max_length=20, editable=False)
    item_code = models.ForeignKey('TankItem', on_delete=models.PROTECT, null=True)      
    tank_capacity = models.DecimalField(max_digits=10, decimal_places=2)
    current_capacity = models.DecimalField(blank=True, null=True, max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'tank_data'
        
    def save(self, *args, **kwargs):
        if not self.tank_code:
            with transaction.atomic(): 
                existing_tanks = TankData.objects.select_for_update().values_list('tank_code', flat=True)
                existing_numbers = set()

                for code in existing_tanks:
                    try:
                        num = int(code.replace('TNK', ''))
                        existing_numbers.add(num)
                    except ValueError:
                        continue 

                next_number = 1
                while next_number in existing_numbers:
                    next_number += 1
                
                self.tank_code = f"TNK{next_number:03d}"
                
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.tank_code} - {self.item_code}"