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