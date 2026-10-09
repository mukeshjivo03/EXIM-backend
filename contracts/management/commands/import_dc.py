"""Import the DC workbook into domestic_contract_details.

    python manage.py import_dc "D C.xlsx"
    python manage.py import_dc "D C.xlsx" --dry-run

Parsing and upsert rules live in contracts/services.py (shared with the upload API).
"""

import os
from decimal import Decimal

from django.core.management.base import BaseCommand, CommandError

from contracts.services import DCImportError, import_dc_workbook


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
        path = options['path']
        if not os.path.exists(path):
            raise CommandError(f"File not found: {path}")

        try:
            result = import_dc_workbook(
                path,
                os.path.basename(path),
                sheet=options['sheet'],
                dry_run=options['dry_run'],
                keep_partial=options['keep_partial'],
                tolerance=Decimal(str(options['tolerance'])),
            )
        except DCImportError as exc:
            raise CommandError(str(exc))

        self._report(result)

        if result.errors:
            raise CommandError(f"{len(result.errors)} row(s) failed to parse — nothing was written.")
        if options['dry_run']:
            self.stdout.write(self.style.WARNING(f"Dry run — {result.parsed} row(s) parsed, nothing written."))
            return
        self.stdout.write(self.style.SUCCESS(
            f"Imported {result.parsed} row(s) from {result.source_file}: "
            f"{result.created} created, {result.updated} updated."
        ))

    def _report(self, result):
        self.stdout.write(f"Parsed {result.parsed} row(s).")
        if result.skipped:
            verb = "Imported with gaps" if result.keep_partial else "Skipped"
            self.stdout.write(self.style.WARNING(f"{verb}: {len(result.skipped)} problem(s) with incomplete data:"))
            for line in result.skipped:
                self.stdout.write(f"  {line}")
            if not result.keep_partial:
                self.stdout.write("  (pass --keep-partial to import these with the bad columns left empty)")
        if result.mismatches:
            self.stdout.write(self.style.WARNING(
                f"{len(result.mismatches)} calculated value(s) differ from the sheet (computed value stored):"
            ))
            for line in result.mismatches:
                self.stdout.write(f"  {line}")
        if result.errors:
            self.stdout.write(self.style.ERROR(f"{len(result.errors)} row(s) could not be parsed:"))
            for line in result.errors:
                self.stdout.write(f"  {line}")
