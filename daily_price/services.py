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

    # Find "Commodities"
    start_row, start_col = None, None
    for r_idx, row in enumerate(reader):
        for c_idx, cell in enumerate(row):
            if "Commodities" in cell:
                start_row, start_col = r_idx, c_idx
                break
        if start_row is not None: break

    if start_row is None: return []

    final_data = []
    for i in range(1, 13):
        try:
            row = reader[start_row + i]
            
            # Helper function to safely convert string to Decimal
            def clean_dec(val):
                if not val or not str(val).strip():
                    return Decimal('0.00')
                try:
                    # Remove currency symbols or commas
                    clean_val = str(val).replace(',', '').strip()
                    return Decimal(clean_val)
                except (InvalidOperation, ValueError):
                    return Decimal('0.00')

            # ADJUSTED INDEXING: 
            # Based on your error log, the data shifted. 
            # We check if start_col+1 is empty and adjust if needed.
            col_offset = start_col
            if not row[col_offset + 1].strip():
                col_offset += 1 # Skip the empty spacer column

            final_data.append({
                "commodity_name": row[start_col].strip(),
                "factory_kg": clean_dec(row[col_offset + 1]),
                "packing_kg": clean_dec(row[col_offset + 2]),
                "gst_kg": clean_dec(row[col_offset + 3]),
                "gst_ltr": clean_dec(row[col_offset + 4]),
                "fetched_date": date.today().isoformat()
            })
        except IndexError:
            continue

    return final_data

