from datetime import datetime

from django.db import transaction
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.permissions import HasAppPermission

from .models import PlanningUpload, PlanningRow
from .serializers import (
    PlanningUploadSerializer,
    PlanningUploadDetailSerializer,
)
from .services.parser import parse_planning_workbook, PlanningParseError

MAX_UPLOAD_BYTES = 10 * 1024 * 1024


class PlanningUploadListCreateView(APIView):
    """GET the upload history; POST a new planning workbook."""

    parser_classes = [MultiPartParser, FormParser]

    def get_permissions(self):
        if self.request.method == "POST":
            return [IsAuthenticated(), HasAppPermission("planning.add_planningupload")]
        return [IsAuthenticated(), HasAppPermission("planning.view_planningupload")]

    def get(self, request):
        uploads = PlanningUpload.objects.all()
        return Response({"uploads": PlanningUploadSerializer(uploads, many=True).data})

    def post(self, request):
        upload_file = request.FILES.get("file")
        if not upload_file:
            return Response({"detail": "No file was uploaded (expected a 'file' field)."}, status=400)
        if not upload_file.name.lower().endswith((".xlsx", ".xlsm")):
            return Response({"detail": "Please upload an .xlsx planning workbook."}, status=400)
        if upload_file.size > MAX_UPLOAD_BYTES:
            return Response({"detail": "That file is larger than the 10 MB limit."}, status=400)

        try:
            month, title, rows, warnings, mismatches = parse_planning_workbook(upload_file)
        except PlanningParseError as exc:
            return Response({"detail": str(exc)}, status=400)
        except Exception as exc:                                  # unreadable / corrupt workbook
            return Response({"detail": "Could not read that workbook: {}".format(exc)}, status=400)

        # The sheet names its own month; an explicit override wins when it is wrong.
        override = request.data.get("month")
        if override:
            try:
                month = datetime.strptime(str(override)[:10], "%Y-%m-%d").date().replace(day=1)
            except ValueError:
                return Response({"detail": "month must be YYYY-MM-DD."}, status=400)
        if month is None:
            return Response(
                {"detail": "Could not tell which month this sheet is for. "
                           "Re-upload with an explicit month."},
                status=400,
            )

        previous = PlanningUpload.objects.filter(month=month).order_by("-version").first()
        version = (previous.version + 1) if previous else 1

        with transaction.atomic():
            upload = PlanningUpload.objects.create(
                month=month,
                version=version,
                title=title,
                source_file=upload_file.name,
                uploaded_by=getattr(request.user, "email", "") or str(request.user),
                notes=request.data.get("notes", "") or "",
            )
            PlanningRow.objects.bulk_create(
                [PlanningRow(upload=upload, **fields) for fields in rows],
                batch_size=500,
            )
            upload.recalculate_totals()
            upload.save()

        return Response(
            {
                "upload": PlanningUploadSerializer(upload).data,
                "warnings": warnings,
                "mismatches": mismatches,
                "replaced_version": previous.version if previous else None,
            },
            status=201,
        )


class PlanningUploadDetailView(APIView):
    """GET one version with its rows; DELETE removes that version."""

    def get_permissions(self):
        if self.request.method == "DELETE":
            return [IsAuthenticated(), HasAppPermission("planning.delete_planningupload")]
        return [IsAuthenticated(), HasAppPermission("planning.view_planningupload")]

    def get(self, request, pk):
        try:
            upload = PlanningUpload.objects.prefetch_related("rows").get(pk=pk)
        except PlanningUpload.DoesNotExist:
            return Response({"detail": "No such planning upload."}, status=404)
        return Response(PlanningUploadDetailSerializer(upload).data)

    def delete(self, request, pk):
        try:
            upload = PlanningUpload.objects.get(pk=pk)
        except PlanningUpload.DoesNotExist:
            return Response({"detail": "No such planning upload."}, status=404)
        label = str(upload)
        upload.delete()
        return Response({"deleted": label})


class PlanningLatestView(APIView):
    """The newest version of the most recent month - the report's default view."""

    def get_permissions(self):
        return [IsAuthenticated(), HasAppPermission("planning.view_planningupload")]

    def get(self, request):
        upload = PlanningUpload.objects.prefetch_related("rows").first()
        if upload is None:
            return Response({"detail": "No planning has been uploaded yet."}, status=404)
        return Response(PlanningUploadDetailSerializer(upload).data)
