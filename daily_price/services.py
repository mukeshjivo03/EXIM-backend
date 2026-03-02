import csv
import requests
from io import StringIO
from datetime import date
from decimal import Decimal, InvalidOperation

def fetch_table_manually():
    URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vR2LwtfXKkkDiVzOc_T591-4KWwUvKW-ZaJokeixIzHkOyHNSjGv5Ilh3597ZgaMA/pub?gid=655973128&single=true&output=csv"
    response = requests.get(URL)
    f = StringIO(response.text)
    reader = list(csv.reader(f))

    # 1. Find the Anchor
    start_row, start_col = None, None
    for r_idx, row in enumerate(reader):
        for c_idx, cell in enumerate(row):
            if "Commodities" in cell:
                start_row, start_col = r_idx, c_idx
                break
        if start_row is not None: break

    if start_row is None: return []

    def clean_dec(val):
        if not val or not str(val).strip(): return Decimal('0.00')
        try:
            return Decimal(str(val).replace(',', '').strip())
        except (InvalidOperation, ValueError): return Decimal('0.00')

    final_data = []
    for i in range(1, 13): # The 12 items in your list
        try:
            row = reader[start_row + i]
            
            # We skip every other column due to the thin separators in your sheet
            final_data.append({
                "commodity_name": row[start_col].strip(),
                "factory_kg":     clean_dec(row[start_col + 2]),
                "packing_kg":     clean_dec(row[start_col + 4]),
                "gst_kg":         clean_dec(row[start_col + 6]),
                "gst_ltr":        clean_dec(row[start_col + 8]),
                "fetched_date":   date.today().isoformat()
            })
        except IndexError:
            continue
    return final_data