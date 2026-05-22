from .models import StockStatus
from django_filters import rest_framework as filters
from stock.models import StockStatus    
from tank.models import TankItem
from sap_sync.models import Party

class StockStatusFilters(filters.FilterSet):
    status = filters.MultipleChoiceFilter(choices=StockStatus.STATUS_CHOICES)

    vendor = filters.ModelMultipleChoiceFilter(
        field_name='vendor_code',           # FK field on StockStatus
        queryset=Party.objects.all(),
        to_field_name='card_code',          # matches to_field='card_code' on your FK
    )

    item = filters.ModelMultipleChoiceFilter(
        field_name='item_code',
        queryset=TankItem.objects.all(),
        to_field_name='tank_item_code',     # matches to_field='tank_item_code' on your FK
    )

    class Meta:
        model = StockStatus
        fields = ['status', 'vendor', 'item']