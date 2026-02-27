from .models import StockStatus
from django_filters import rest_framework as filters


class StockStatusFilters(filters.FilterSet):
    status = filters.ChoiceFilter(choices=StockStatus.STATUS_CHOICES)
    vendor = filters.CharFilter(field_name='vendor_code__card_code')
    item = filters.CharFilter(field_name='item_code__item_code')

    class Meta:
        model = StockStatus
        fields = ['status', 'vendor_code', 'item_code']