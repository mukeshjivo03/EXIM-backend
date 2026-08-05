"""Import the DC workbook into domestic_contract_details.

    python manage.py import_dc "D C.xlsx"
    python manage.py import_dc "D C.xlsx" --dry-run

Idempotent: rows upsert on invoice_no, so re-running an updated sheet refreshes
existing records instead of duplicating them. Calculated columns are recomputed
from the raw inputs; any workbook value that disagrees beyond --tolerance is
reported as a mismatch (the computed value is what gets stored).

Rows with unreadable optional cells (a mistyped date, a blank PO) are listed and
skipped, so nothing lands half-populated. Pass --keep-partial to import them with
those columns left empty instead.
"""

import os
from datetime import datetime
from decimal import Decimal, InvalidOperation

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from contracts.models import DomesticContractDetails


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

UPDATE_FIELDS = RAW_FIELDS + DERIVED_FIELDS + ['source_file', 'source_row']


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


class Command(BaseCommand):
    help = "Import the DC workbook into domestic_contract_details (upsert on invoice number)."

    def add_arguments(self, parser):
        parser.add_argument('path', help='Path to the DC .xlsx file')
        parser.add_argument('--sheet', default=None, help='Sheet name (default: first sheet)')
        parser.add_argument('--dry-run', action='store_true',
                            help='Parse, validate and report — write nothing')
        parser.add_argument('--tolerance', type=float, default=0.5,
                            help='Allowed absolute drift between sheet and recomputed values (default 0.5)')
        parser.add_argument('--keep-partial', action='store_true',
                            help='Import rows with unreadable optional cells anyway, leaving those '
                                 'columns empty (default: skip them)')

    def handle(self, *args, **options):
        try:
            import openpyxl
        except ImportError:
            raise CommandError("openpyxl is required: pip install openpyxl")

        path = options['path']
        if not os.path.exists(path):
            raise CommandError(f"File not found: {path}")

        workbook = openpyxl.load_workbook(path, data_only=True, read_only=True)
        sheet = workbook[options['sheet']] if options['sheet'] else workbook.worksheets[0]

        rows = list(sheet.iter_rows(values_only=True))
        if not rows:
            raise CommandError("Workbook is empty")
        self._check_headers(rows[0])

        tolerance = Decimal(str(options['tolerance']))
        source_file = os.path.basename(path)

        records, errors, skipped, mismatches = [], [], [], []
        seen_invoices = {}

        for offset, row in enumerate(rows[1:], start=2):
            if not any(cell not in (None, '') for cell in row):
                continue                                   # trailing blank row

            defects = []
            try:
                record = self._build(row, source_file, offset, defects)
            except ValueError as exc:
                errors.append(f"row {offset}: {exc}")
                continue

            if defects:
                skipped.extend(defects)
                if not options['keep_partial']:
                    continue

            first_seen = seen_invoices.get(record.invoice_no)
            if first_seen:
                errors.append(f"row {offset}: invoice {record.invoice_no} duplicates row {first_seen}")
                continue
            seen_invoices[record.invoice_no] = offset

            mismatches.extend(self._compare(row, record, tolerance, offset))
            records.append(record)

        self._report(mismatches, skipped, errors, len(records), options['keep_partial'])

        if errors:
            raise CommandError(f"{len(errors)} row(s) failed to parse — nothing was written.")

        if options['dry_run']:
            self.stdout.write(self.style.WARNING(f"Dry run — {len(records)} row(s) parsed, nothing written."))
            return

        existing = set(
            DomesticContractDetails.objects
            .filter(invoice_no__in=list(seen_invoices))
            .values_list('invoice_no', flat=True)
        )

        with transaction.atomic():
            DomesticContractDetails.objects.bulk_create(
                records,
                batch_size=500,
                update_conflicts=True,
                unique_fields=['invoice_no'],
                update_fields=UPDATE_FIELDS,
            )

        created = len(records) - len(existing)
        self.stdout.write(self.style.SUCCESS(
            f"Imported {len(records)} row(s) from {source_file}: {created} created, {len(existing)} updated."
        ))

    # ------------------------------------------------------------------ helpers

    def _check_headers(self, header_row):
        for index, expected in EXPECTED_HEADERS.items():
            actual = str(header_row[index]).strip() if index < len(header_row) and header_row[index] else ''
            if actual.upper() != expected.upper():
                raise CommandError(
                    f"Unexpected layout: column {index} is {actual!r}, expected {expected!r}. "
                    "The importer binds columns by position — update COL in import_dc.py if the sheet changed."
                )

    def _build(self, row, source_file, source_row, defects):
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

    def _compare(self, row, record, tolerance, source_row):
        """Flag workbook values that disagree with what we recomputed."""
        found = []
        for field in DERIVED_FIELDS:
            index = COL[field]
            try:
                sheet_value = parse_decimal(row[index] if index < len(row) else None)
            except ValueError:
                sheet_value = None
            computed = getattr(record, field)
            if sheet_value is None or computed is None:
                continue
            if abs(sheet_value - computed) > tolerance:
                found.append(
                    f"row {source_row} ({record.invoice_no}) {field}: "
                    f"sheet {sheet_value:,.4f} vs computed {computed:,.4f}"
                )
        return found

    def _report(self, mismatches, skipped, errors, parsed, keep_partial):
        self.stdout.write(f"Parsed {parsed} row(s).")
        if skipped:
            verb = "Imported with gaps" if keep_partial else "Skipped"
            self.stdout.write(self.style.WARNING(f"{verb}: {len(skipped)} row(s) with incomplete data:"))
            for line in skipped:
                self.stdout.write(f"  {line}")
            if not keep_partial:
                self.stdout.write("  (pass --keep-partial to import these with the bad columns left empty)")
        if mismatches:
            self.stdout.write(self.style.WARNING(
                f"{len(mismatches)} calculated value(s) differ from the sheet (computed value stored):"
            ))
            for line in mismatches:
                self.stdout.write(f"  {line}")
        if errors:
            self.stdout.write(self.style.ERROR(f"{len(errors)} row(s) could not be parsed:"))
            for line in errors:
                self.stdout.write(f"  {line}")
