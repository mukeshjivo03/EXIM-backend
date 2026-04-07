from django.db import models

# Create your models here.
class DailyPrice(models.Model):
    commodity_name = models.CharField(max_length=125)
    factory_price = models.DecimalField(max_digits=6 , decimal_places = 2)
    packing_cost_kg = models.DecimalField(max_digits=6 , decimal_places = 2)
    with_gst_kg = models.DecimalField(max_digits=6 , decimal_places = 2)
    with_gst_ltr = models.DecimalField(max_digits=6 , decimal_places = 2)

    date = models.DateField()
    created_by = models.CharField(max_length=50,)

    class Meta:
        unique_together = ('commodity_name' , 'date')
        db_table  = 'daily_prices'
        permissions = [
            ("fetch_daily_price" , "Can fetch Daily Prices"),
            ("view_daily_price_graph" , "Can see daily price grpah")
        ]



class JivoRates(models.Model):
    pack_type = models.CharField(max_length=125 , blank=True , null =True)
    commodity = models.CharField(max_length=125 , blank=True , null =True)
    rate = models.DecimalField(max_digits=10 , decimal_places = 3     , blank = True , null = True)
    
    date = models.DateField()
    created_by = models.CharField(max_length=50)   
    
    def __str__(self):
        return f"{self.commodity} - {self.rate}"
    
    class Meta:
        db_table  = 'jivo_rates'
        permissions = [
            ("fetch_jivo_rate"  , "Can fetch jivo rates"),
        ]