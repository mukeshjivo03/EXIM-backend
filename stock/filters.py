from .models import StockStatus
from django_filters import rest_framework as filters


class StockStatusFilters(filters.FilterSet):
    status = filters.ChoiceFilter(choices=StockStatus.STATUS_CHOICES)
    
    # Matches card_code in your Party model
    vendor = filters.CharFilter(field_name='vendor_code__card_code')
    
    # Matches tank_item_code in TankItem model (FK to_field)
    item = filters.CharFilter(field_name='item_code__tank_item_code')

    class Meta:
        model = StockStatus
        fields = ['status']