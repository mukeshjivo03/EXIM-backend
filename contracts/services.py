"""Parse the DC workbook and upsert it into domestic_contract_details.

Used by both the `import_dc` management command and the upload API.

Idempotent: rows upsert on invoice_no, so re-importing an updated sheet refreshes
existing records instead of duplicating them. Calculated columns are recomputed
from the raw inputs; any workbook value that disagrees beyond `tolerance` is
reported as a mismatch (the computed value is what gets stored).

Rows with unreadable optional cells (a mistyped date, a blank PO) are reported and
skipped, so nothing lands half-populated, unless `keep_partial` is set — then they
are imported with those columns left empty. Any row that cannot be parsed at all
aborts the import: nothing is written.
"""

from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal, InvalidOperation

from django.db import transaction

from .models import DomesticContractDetails


class DCImportError(Exception):
    """The workbook as a whole can't be imported (empty, wrong layout, unreadable)."""


# Workbook column index -> meaning. The sheet has an unnamed leading status column
# and two columns both headed "COST in LTR" (per-KL and per-litre), so we bind by
# position and validate the header row rather than matching on names.
COL = {
    'status': 0,
    'supplier': 1,
    'po_number': 2,
    'del_terms': 3,
    'contract_qty': 4,
    'invoice_no': 5,
    'invoice_date': 6,
    'grpo_date': 7,
    'item': 8,
    'load_qty_mts': 9,
    'inv_rate': 10,
    'basic_amount': 11,
    'unload_qty_mts': 12,
    'unload_qty_ltr': 13,
    'rate_in_sap_unloading': 14,
    'shortage_recd_mts': 15,
    'allow_shortage_mts': 16,
    'deduction_qty_mts': 17,
    'deduct_amount': 18,
    'freight_rate': 19,
    'freight_amount': 20,
    'brokerage_rate': 21,
    'brokerage_amount': 22,
    'cost_per_mt': 23,
    'cost_per_kl': 24,
    'cost_per_ltr': 25,
    'transporter_name': 26,
    'vehicle_number': 27,
    'bilty_number': 28,
    'grpo_no': 29,
    'bilty_charges': 30,
}

EXPECTED_HEADERS = {
    1: 'SUPPLIER',
    2: 'PURCHASE ORDER',
    5: 'INV NUMBER',
    9: 'LOAD QTY (MTS)',
    12: 'UNLOAD QTY (MTS)',
    23: 'COST in KGS',
    29: 'GRPO',
}

RAW_FIELDS = [
    'status', 'supplier', 'po_number', 'del_terms', 'contract_qty',
    'invoice_no', 'invoice_date', 'grpo_date', 'grpo_no', 'item',
    'load_qty_mts', 'inv_rate', 'unload_qty_mts', 'unload_qty_ltr',
    'freight_rate', 'brokerage_rate', 'bilty_charges',
    'transporter_name', 'vehicle_number', 'bilty_number',
]

# Recomputed on import and cross-checked against the sheet.
DERIVED_FIELDS = [
    'basic_amount', 'rate_in_sap_unloading', 'shortage_recd_mts',
    'allow_shortage_mts', 'deduction_qty_mts', 'deduct_amount',
    'freight_amount', 'brokerage_amount',
    'cost_per_mt', 'cost_per_kl', 'cost_per_ltr',
]

UPDATE_FIELDS = RAW_FIELDS + DERIVED_FIELDS + ['source_file', 'source_row', 'updated_at']


KG_PER_MT = Decimal('1000')


def parse_decimal(value):
    """Accept 41.55, '1,47,000' (Indian grouping), '2000 KG', '' and None.

    Small parcels are written in kilos in the quantity columns ('600 KG' against
    a load qty of 0.6) — those are converted to MT so one unit is stored.
    """
    if value is None:
        return None
    if isinstance(value, (int, float, Decimal)):
        return Decimal(str(value))

    text = str(value).strip().replace(',', '')
    if not text:
        return None

    divisor = Decimal('1')
    upper = text.upper()
    for suffix, factor in (('KGS', KG_PER_MT), ('KG', KG_PER_MT), ('MTS', Decimal('1')), ('MT', Decimal('1'))):
        if upper.endswith(suffix):
            text, divisor = upper[:-len(suffix)].strip(), factor
            break
    try:
        return Decimal(text) / divisor
    except InvalidOperation:
        raise ValueError(f"not a number: {value!r}")


def parse_date(value):
    """The sheet mixes dd.mm.yy and dd.mm.yyyy, real datetimes, and typos.

    Repeated separators ('24..05.26') are collapsed. Anything still ambiguous —
    notably '02.25.26', where neither day-first nor month-first is plausible —
    raises rather than being guessed at.
    """
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.date()
    if hasattr(value, 'year'):
        return value

    text = str(value).strip()
    if not text:
        return None
    for separator in ('.', '/', '-'):
        while separator * 2 in text:
            text = text.replace(separator * 2, separator)

    for fmt in ('%d.%m.%Y', '%d.%m.%y', '%d/%m/%Y', '%d/%m/%y', '%Y-%m-%d', '%d-%m-%Y', '%d-%m-%y'):
        try:
            return datetime.strptime(text, fmt).date()
        except ValueError:
            continue
    raise ValueError(f"unrecognised date: {value!r}")


def parse_text(value):
    if value is None:
        return None
    text = str(value).strip()
    if text.endswith('.0') and text[:-2].isdigit():
        text = text[:-2]           # numeric cells such as bilty / invoice numbers
    return text or None


@dataclass
class DCImportResult:
    source_file: str
    parsed: int = 0                                 # rows that will be / were written
    created: int = 0
    updated: int = 0
    written: bool = False
    keep_partial: bool = False
    skipped: list = field(default_factory=list)     # optional-cell problems (row skipped unless keep_partial)
    mismatches: list = field(default_factory=list)  # sheet value differs from recomputed value
    errors: list = field(default_factory=list)      # rows that could not be parsed — blocks the import

    def as_dict(self):
        return {
            'source_file': self.source_file,
            'parsed': self.parsed,
            'created': self.created,
            'updated': self.updated,
            'written': self.written,
            'keep_partial': self.keep_partial,
            'skipped': self.skipped,
            'mismatches': self.mismatches,
            'errors': self.errors,
        }


def import_dc_workbook(file, source_file, *, sheet=None, dry_run=False, keep_partial=False, tolerance=Decimal('0.5')):
    """Parse the workbook (a path or file-like object) and upsert it unless `dry_run`.

    Nothing is written when any row fails to parse; the result lists why.
    Raises DCImportError when the workbook itself can't be used.
    """
    try:
        import openpyxl
        workbook = openpyxl.load_workbook(file, data_only=True, read_only=True)
    except Exception as exc:
        raise DCImportError(f"Could not read that workbook: {exc}")

    try:
        try:
            worksheet = workbook[sheet] if sheet else workbook.worksheets[0]
        except KeyError:
            raise DCImportError(f"No sheet named {sheet!r} in the workbook")
        rows = list(worksheet.iter_rows(values_only=True))
    finally:
        workbook.close()

    if not rows:
        raise DCImportError("The workbook is empty")
    _check_headers(rows[0])

    result = DCImportResult(source_file=source_file, keep_partial=keep_partial)
    records, seen_invoices = [], {}

    for offset, row in enumerate(rows[1:], start=2):
        if not any(cell not in (None, '') for cell in row):
            continue                                   # trailing blank row

        defects = []
        try:
            record = _build(row, source_file, offset, defects)
        except ValueError as exc:
            result.errors.append(f"row {offset}: {exc}")
            continue

        if defects:
            result.skipped.extend(defects)
            if not keep_partial:
                continue

        first_seen = seen_invoices.get(record.invoice_no)
        if first_seen:
            result.errors.append(f"row {offset}: invoice {record.invoice_no} duplicates row {first_seen}")
            continue
        seen_invoices[record.invoice_no] = offset

        result.mismatches.extend(_compare(row, record, tolerance, offset))
        records.append(record)

    result.parsed = len(records)
    existing = set(
        DomesticContractDetails.objects
        .filter(invoice_no__in=list(seen_invoices))
        .values_list('invoice_no', flat=True)
    )
    result.updated = len(existing)
    result.created = len(records) - len(existing)

    if result.errors or dry_run or not records:
        return result

    with transaction.atomic():
        DomesticContractDetails.objects.bulk_create(
            records,
            batch_size=500,
            update_conflicts=True,
            unique_fields=['invoice_no'],
            update_fields=UPDATE_FIELDS,
        )
    result.written = True
    return result


def _check_headers(header_row):
    for index, expected in EXPECTED_HEADERS.items():
        actual = str(header_row[index]).strip() if index < len(header_row) and header_row[index] else ''
        if actual.upper() != expected.upper():
            raise DCImportError(
                f"Unexpected layout: column {index + 1} is {actual or 'empty'!r}, expected {expected!r}. "
                "Use the standard DC workbook layout (columns are read by position)."
            )


def _build(row, source_file, source_row, defects):
    """Build one record, appending any optional-cell problems to `defects`.

    A row raises outright only when it cannot be identified (no invoice
    number) or a figure feeding the cost calculation is unreadable — those
    abort the whole import. Optional-cell problems are collected instead, and
    the caller decides whether to skip the row or keep it with gaps.
    """
    def cell(name):
        index = COL[name]
        return row[index] if index < len(row) else None

    def soft(name, parser):
        """Parse an optional cell; on failure record the defect and carry on."""
        try:
            return parser(cell(name))
        except ValueError as exc:
            defects.append(f"row {source_row}: {name} {exc}")
            return None

    invoice_no = parse_text(cell('invoice_no'))
    if not invoice_no:
        raise ValueError("missing invoice number")

    po_number = parse_text(cell('po_number'))
    if not po_number:
        defects.append(f"row {source_row}: missing purchase order")
        po_number = ''

    record = DomesticContractDetails(
        invoice_no=invoice_no,
        invoice_date=soft('invoice_date', parse_date),
        po_number=po_number,
        grpo_no=parse_text(cell('grpo_no')),
        grpo_date=soft('grpo_date', parse_date),
        status=parse_text(cell('status')),
        supplier=parse_text(cell('supplier')) or '',
        item=parse_text(cell('item')) or '',
        del_terms=parse_text(cell('del_terms')),
        contract_qty=soft('contract_qty', parse_decimal),
        # these four drive every derived amount, so a bad value is fatal
        load_qty_mts=parse_decimal(cell('load_qty_mts')),
        inv_rate=parse_decimal(cell('inv_rate')),
        unload_qty_mts=parse_decimal(cell('unload_qty_mts')),
        unload_qty_ltr=parse_decimal(cell('unload_qty_ltr')),
        freight_rate=parse_decimal(cell('freight_rate')),
        brokerage_rate=parse_decimal(cell('brokerage_rate')),
        bilty_charges=soft('bilty_charges', parse_decimal),
        transporter_name=parse_text(cell('transporter_name')),
        vehicle_number=parse_text(cell('vehicle_number')),
        bilty_number=parse_text(cell('bilty_number')),
        source_file=source_file,
        source_row=source_row,
    )
    return record.recalculate()


def _compare(row, record, tolerance, source_row):
    """Flag workbook values that disagree with what we recomputed."""
    found = []
    for name in DERIVED_FIELDS:
        index = COL[name]
        try:
            sheet_value = parse_decimal(row[index] if index < len(row) else None)
        except ValueError:
            sheet_value = None
        computed = getattr(record, name)
        if sheet_value is None or computed is None:
            continue
        if abs(sheet_value - computed) > tolerance:
            found.append(
                f"row {source_row} ({record.invoice_no}) {name}: "
                f"sheet {sheet_value:,.4f} vs computed {computed:,.4f}"
            )
    return found
