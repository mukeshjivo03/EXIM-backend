from django.db import models
from decimal import Decimal

LTR_CONVERSION = Decimal('1.0989')


class CommodityMargin(models.Model):
    commodity = models.CharField(max_length=100)
    margin_rate = models.DecimalField(max_digits=5, decimal_places=2 , blank=True , null=True)
    created_at = models.DateTimeField(auto_now=True)
    created_by = models.CharField(max_length=255)

    class Meta:
        db_table = 'commodity_rates'


class MarketRates(models.Model):
    commodity = models.ForeignKey(CommodityMargin , on_delete=models.SET_NULL , null = True)
    factory_kg = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField(auto_now_add=True)
    created_by = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.commodity}: {self.margin_rate}"

    class Meta:
        db_table = 'market_rates'
        unique_together = ('commodity', 'date')

    @property
    def with_packing(self) -> Decimal:
        return Decimal(self.factory_kg) + Decimal('14')
    
    @property
    def with_gst_kg(self) -> Decimal:
        return self.with_packing + (Decimal('0.05') * self.with_packing)
    
    @property
    def with_gst_ltr(self) -> Decimal:
        return self.with_gst_kg / Decimal('1.0989')
    
    class Meta:
        db_table = 'market_rates'


class PackingMargins(models.Model):
    packing_name = models.CharField(max_length=100)
    packing_margin = models.DecimalField(max_digits=10 , decimal_places=5)
    created_by = models.CharField(max_length=10)
    created_at = models.DateField(auto_now_add=True)

    class Meta:
        db_table = 'packing_margins'

class BasicRates(models.Model):
    packing_type = models.ForeignKey(PackingMargins , on_delete=models.SET_NULL , null = True)
    market_rate = models.ForeignKey(MarketRates , on_delete=models.SET_NULL, null = True)
    basic_price_kg = models.DecimalField(max_digits=10 , decimal_places=3)
    date = models.DateField(auto_now_add=True)

    @property
    def basic_price_ltr(self) -> Decimal:
        return self.basic_price_kg / LTR_CONVERSION

    class Meta:
        db_table = 'basic_rates'


class PackSize(models.Model):
    UNIT_KG = 'kg'
    UNIT_LTR = 'ltr'
    UNIT_CHOICES = (
        (UNIT_KG, 'Kg'),
        (UNIT_LTR, 'Ltr'),
    )

    name = models.CharField(max_length=100)
    packing = models.ForeignKey(PackingMargins, on_delete=models.CASCADE)
    unit = models.CharField(max_length=3, choices=UNIT_CHOICES)
    conversion_factor = models.DecimalField(max_digits=10, decimal_places=5)
    commodities = models.ManyToManyField(CommodityMargin, blank=True)
    display_order = models.PositiveIntegerField(default=0)
    created_by = models.CharField(max_length=255)
    created_at = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.name

    def rate_from_basic_kg(self, basic_price_kg: Decimal) -> Decimal:
        if self.unit == self.UNIT_LTR:
            return (Decimal(basic_price_kg) / LTR_CONVERSION) * self.conversion_factor
        return Decimal(basic_price_kg) * self.conversion_factor

    class Meta:
        db_table = 'pack_sizes'
        ordering = ['display_order', 'id']


class PackRates(models.Model):
    market_rate = models.ForeignKey(MarketRates, on_delete=models.CASCADE, related_name='pack_rates')
    pack_size = models.ForeignKey(PackSize, on_delete=models.SET_NULL, null=True)
    rate = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField(auto_now_add=True)

    class Meta:
        db_table = 'pack_rates'



