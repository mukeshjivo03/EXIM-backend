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
                "fetched_date":   date.today().isoformat(),
            })
        except IndexError:
            continue
    return final_data


def fetch_jivo_rates(creator_name="System"):
    url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vR2LwtfXKkkDiVzOc_T591-4KWwUvKW-ZaJokeixIzHkOyHNSjGv5Ilh3597ZgaMA/pub?gid=655973128&single=true&output=csv"
    
    # 1. Fetch the CSV data
    response = requests.get(url)
    response.raise_for_status() # Ensure the request was successful
    
    # 2. Parse the CSV
    lines = response.text.splitlines()
    reader = csv.reader(lines)
    
    # Define what we are looking for (Anchors)
    target_packs = [
        '15 Ltr Tin', 'Pouch 1 Ltr', '15 Kg Tin NP', 
        'Pouch 750 Gm', 'Pouch 700 Gm', 'Bottle 1 Ltr', '5 Ltr Jar'
    ]
    
    # Define where the prices are relative to the anchor (Column offsets)
    # Based on your CSV structure: Pouch 1 Ltr is at index i, Soya is i+1, Mustard is i+3, Sunflower is i+5
    commodities_offsets = [
        ('SOYA', 1),
        ('Mustard', 3),
        ('Sunflower', 5)
    ]
    
    today = date.today()
    rates_to_create = []

    # 3. Iterate through rows to find anchors
    for row in reader:
        for i, cell in enumerate(row):
            clean_cell = cell.strip()
            
            # If we hit a recognized pack type (e.g., "Pouch 1 Ltr")
            if clean_cell in target_packs:
                
                # Extract rates for each commodity based on the offset
                for commodity, offset in commodities_offsets:
                    target_index = i + offset
                    
                    # Ensure we don't get an IndexError if the row is short
                    if target_index < len(row):
                        rate_str = row[target_index].strip()
                        
                        # If there is an actual rate value present
                        if rate_str: 
                            try:
                                # Clean commas if any exist (e.g., "1,200.50")
                                rate_val = float(rate_str.replace(',', ''))
                                
                                rates_to_create.append(
                                    {
                                        "pack_type":clean_cell,
                                        "commodity":commodity,
                                        "rate":rate_val,
                                        "date":today,
                                        "created_by":creator_name
                                    }
                                )
                            except ValueError:
                                # Ignore cells that have text instead of numbers
                                pass 
    
    return rates_to_create