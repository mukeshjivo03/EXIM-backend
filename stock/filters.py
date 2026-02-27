class StockStatusFilters(filters.FilterSet):
    status = filters.ChoiceFilter(choices=StockStatus.STATUS_CHOICES)
    
    # Matches card_code in the Party model
    vendor = filters.CharFilter(field_name='vendor_code__card_code')
    
    # Matches item_code in the RMProducts model
    item = filters.CharFilter(field_name='item_code__item_code')

    class Meta:
        model = StockStatus
        fields = ['status', 'vendor_code', 'item_code']