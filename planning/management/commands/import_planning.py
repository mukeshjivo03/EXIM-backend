"""Load a planning workbook from the command line.

    python manage.py import_planning "PLANNING FOR SEP 2026.xlsx"
    python manage.py import_planning sheet.xlsx --month 2026-09-01 --dry-run

Same parser the upload endpoint uses, so a backfill of older months behaves
exactly like an upload through the UI. Each run adds a new version for its month.
"""

from datetime import datetime

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from planning.models import PlanningUpload, PlanningRow
from planning.services.parser import parse_planning_workbook, PlanningParseError


class Command(BaseCommand):
    help = "Import a monthly planning workbook as a new version."

    def add_arguments(self, parser):
        parser.add_argument("path", help="Path to the planning .xlsx file")
        parser.add_argument("--sheet", default=None, help="Sheet name (default: first sheet)")
        parser.add_argument("--month", default=None,
                            help="Override the month the sheet names, as YYYY-MM-DD")
        parser.add_argument("--uploaded-by", default="management-command")
        parser.add_argument("--notes", default="")
        parser.add_argument("--dry-run", action="store_true",
                            help="Parse and report without writing anything")

    def handle(self, *args, **options):
        try:
            month, title, rows, warnings, mismatches = parse_planning_workbook(
                options["path"], sheet_name=options["sheet"]
            )
        except PlanningParseError as exc:
            raise CommandError(str(exc))
        except FileNotFoundError:
            raise CommandError("File not found: {}".format(options["path"]))

        if options["month"]:
            try:
                month = datetime.strptime(options["month"], "%Y-%m-%d").date().replace(day=1)
            except ValueError:
                raise CommandError("--month must be YYYY-MM-DD")
        if month is None:
            raise CommandError(
                "Could not tell which month this sheet is for - pass --month YYYY-MM-DD."
            )

        self.stdout.write("Month : {:%B %Y}".format(month))
        self.stdout.write("Title : {}".format(title or "-"))
        self.stdout.write("Rows  : {}".format(len(rows)))

        if warnings:
            self.stdout.write(self.style.WARNING("{} warning(s):".format(len(warnings))))
            for line in warnings:
                self.stdout.write("  " + line)
        if mismatches:
            self.stdout.write(self.style.WARNING(
                "{} figure(s) differ from the sheet (computed value stored):".format(len(mismatches))
            ))
            for line in mismatches:
                self.stdout.write("  " + line)

        if options["dry_run"]:
            self.stdout.write(self.style.WARNING("Dry run - nothing written."))
            return

        previous = PlanningUpload.objects.filter(month=month).order_by("-version").first()
        version = (previous.version + 1) if previous else 1

        with transaction.atomic():
            upload = PlanningUpload.objects.create(
                month=month,
                version=version,
                title=title,
                source_file=options["path"].replace("\\", "/").split("/")[-1],
                uploaded_by=options["uploaded_by"],
                notes=options["notes"],
            )
            PlanningRow.objects.bulk_create(
                [PlanningRow(upload=upload, **fields) for fields in rows], batch_size=500
            )
            upload.recalculate_totals()
            upload.save()

        self.stdout.write(self.style.SUCCESS(
            "Imported {} as version {} - {} rows, total {:,}".format(
                upload, version, upload.row_count, upload.grand_total
            )
        ))
