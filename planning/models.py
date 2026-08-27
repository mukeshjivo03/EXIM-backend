from decimal import Decimal

from django.db import models


class PlanningUpload(models.Model):
    """One uploaded planning workbook — a single version of one month's plan.

    Planning gets revised mid-month, so a month can hold several versions.
    The highest version for a month is the live one; earlier ones stay for history.
    """

    month = models.DateField(help_text="First day of the planned month, e.g. 2026-09-01")
    version = models.PositiveIntegerField(default=1)
    title = models.CharField(max_length=255, blank=True, help_text="Banner text from the sheet")

    source_file = models.CharField(max_length=255)
    uploaded_by = models.CharField(max_length=150, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)

    row_count = models.IntegerField(default=0)
    commodity_total = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    premium_total = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    ecom_total = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    grand_total = models.DecimalField(max_digits=18, decimal_places=2, default=0)

    class Meta:
        db_table = "planning_uploads"
        ordering = ["-month", "-version"]
        unique_together = ("month", "version")

    def __str__(self):
        return f"{self.month:%b %Y} v{self.version}"

    @property
    def is_latest(self):
        return not PlanningUpload.objects.filter(
            month=self.month, version__gt=self.version
        ).exists()

    def recalculate_totals(self):
        """Roll the row figures up onto the header. Returns self (unsaved)."""
        totals = self.rows.aggregate(
            c=models.Sum("commodity_monthly"),
            p=models.Sum("premium_monthly"),
            e=models.Sum("ecom_planning"),
            t=models.Sum("total_planning"),
        )
        self.commodity_total = totals["c"] or Decimal("0")
        self.premium_total = totals["p"] or Decimal("0")
        self.ecom_total = totals["e"] or Decimal("0")
        self.grand_total = totals["t"] or Decimal("0")
        self.row_count = self.rows.count()
        return self


class PlanningRow(models.Model):
    """One SKU line of a planning sheet.

    The workbook splits the monthly figure across two mutually exclusive column
    blocks — COMMODITY and PREMIUM — chosen by the SKU's HEAD. Both are stored as
    they appear; `total_planning` is recomputed as commodity + premium + ecom.
    """

    upload = models.ForeignKey(PlanningUpload, related_name="rows", on_delete=models.CASCADE)

    # ----------------------------------IDENTITY------------------------------------------
    code = models.CharField(max_length=50, db_index=True)
    brand = models.CharField(max_length=100, blank=True, db_index=True)
    head = models.CharField(max_length=100, blank=True, db_index=True)
    category = models.CharField(max_length=100, blank=True, db_index=True)
    sub_category = models.CharField(max_length=100, blank=True, db_index=True)
    sku = models.CharField(max_length=255, blank=True)

    # ----------------------------------PACK------------------------------------------
    per_ltrs = models.DecimalField(max_digits=12, decimal_places=3, null=True, blank=True)
    ltrs_per_box = models.DecimalField(max_digits=12, decimal_places=3, null=True, blank=True)
    case_pack = models.DecimalField(max_digits=12, decimal_places=3, null=True, blank=True)

    # ----------------------------------COMMODITY BLOCK------------------------------------------
    commodity_monthly = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    commodity_w1 = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    commodity_w2 = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    commodity_w3 = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    commodity_w4 = models.DecimalField(max_digits=18, decimal_places=2, default=0)

    # ----------------------------------PREMIUM BLOCK------------------------------------------
    premium_monthly = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    premium_w1 = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    premium_w2 = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    premium_w3 = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    premium_w4 = models.DecimalField(max_digits=18, decimal_places=2, default=0)

    # ----------------------------------ECOM + TOTAL------------------------------------------
    ecom_planning = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    total_planning = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    # total_planning = commodity_monthly + premium_monthly + ecom_planning

    source_row = models.IntegerField(null=True, blank=True)

    class Meta:
        db_table = "planning_rows"
        ordering = ["-total_planning", "code"]
        indexes = [models.Index(fields=["upload", "category"]),
                   models.Index(fields=["upload", "sub_category"])]

    def __str__(self):
        return f"{self.code} {self.sku}"

    @property
    def monthly_planning(self):
        """Combined monthly figure, whichever block it was recorded in."""
        return (self.commodity_monthly or 0) + (self.premium_monthly or 0)

    def recalculate(self):
        """Derive the weekly and total figures from the raw inputs. Returns self."""
        self.commodity_monthly = (
            self.commodity_w1 + self.commodity_w2 + self.commodity_w3 + self.commodity_w4
        )
        self.premium_monthly = (
            self.premium_w1 + self.premium_w2 + self.premium_w3 + self.premium_w4
        )
        self.total_planning = self.commodity_monthly + self.premium_monthly + self.ecom_planning
        return self
