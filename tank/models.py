from django.db import models

# Create your models here.
class TankItem(models.Model):
    item_code = models.CharField(max_length=50)
    item_name = models.CharField(max_length = 255)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.CharField(max_length=50)
    color = models.CharField(max_length=10)
    
    class Meta:
        db_table = 'tank_item'


class TankData(models.Model):
    tank_number = models.IntegerField()
    item_code = models.ForeignKey(TankItem, on_delete=models.CASCADE)      
    tank_capacity = models.DecimalField(max_digits=10, decimal_places=2)
    current_capacit = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'tank_data'