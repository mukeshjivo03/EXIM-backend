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
    
    response = requests.get(url)
    response.raise_for_status()
    
    # KEY FIX: Don't splitlines() — let csv.reader handle multiline quoted fields
    import io
    rows = list(csv.reader(io.StringIO(response.text)))

    # Find JIVO RATE anchor
    anchor_row, anchor_col = None, None
    for r_idx, row in enumerate(rows):
        for c_idx, cell in enumerate(row):
            if cell.strip() == 'JIVO RATE':
                anchor_row, anchor_col = r_idx, c_idx
                break
        if anchor_row is not None:
            break

    if anchor_row is None:
        raise ValueError("JIVO RATE anchor not found.")

    # Build commodity col map — normalize newlines in cell text
    commodity_aliases = {
        'SOYA': 'SOYA',
        'Mustard': 'Mustard',
        'Sunflower': 'Sunflower',
        'Cotton Refined': 'Cotton Refined',
        'Ricebran Refined': 'Ricebran Refined',
    }

    header_row = rows[anchor_row]
    commodity_col_map = {}
    label_col = anchor_col



    print(f"Anchor: row={anchor_row}, col={anchor_col}")
    print(f"Commodity cols: {commodity_col_map}")

    target_packs = {
        'Pouch 1 Ltr', 'Pouch 750 Gm', 'Pouch 700 Gm',
        'Bottle 1 Ltr', '15 Ltr Tin', '15 Kg Tin', '13 Kg Tin'
    }

    today = date.today()
    rates_to_create = []

    for row in rows[anchor_row + 1:]:
        pack_label = row[label_col].strip()
        if pack_label in target_packs:
            soya_col = commodity_col_map.get('SOYA')
            print(f"{pack_label} | SOYA col={soya_col} | raw value='{row[soya_col]}'")
        for c_idx in range(anchor_col + 1, len(header_row)):
            # Normalize: strip outer whitespace, replace internal newlines with space
            normalized = ' '.join(header_row[c_idx].split())
            if normalized in commodity_aliases:
                commodity_col_map[commodity_aliases[normalized]] = c_idx
                
    for row in rows[anchor_row + 1:]:
        if label_col >= len(row):
            continue
        pack_label = row[label_col].strip()
        if not pack_label or pack_label not in target_packs:
            continue

        for commodity, col_idx in commodity_col_map.items():
            if col_idx >= len(row):
                continue
            rate_str = row[col_idx].strip()
            if not rate_str:
                continue
            try:
                rates_to_create.append({
                    "pack_type": pack_label,
                    "commodity": commodity,
                    "rate": float(rate_str.replace(',', '')),
                    "date": today,
                    "created_by": creator_name
                })
            except ValueError:
                pass

    return rates_to_create