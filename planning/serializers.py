from rest_framework import serializers

from .models import PlanningUpload, PlanningRow


class PlanningRowSerializer(serializers.ModelSerializer):
    """One SKU line. `monthly_planning` folds the two mutually exclusive blocks."""

    monthly_planning = serializers.DecimalField(max_digits=18, decimal_places=2, read_only=True)

    class Meta:
        model = PlanningRow
        exclude = ["upload"]


class PlanningUploadSerializer(serializers.ModelSerializer):
    """Header only - used for the month/version history list."""

    is_latest = serializers.BooleanField(read_only=True)

    class Meta:
        model = PlanningUpload
        fields = "__all__"


class PlanningUploadDetailSerializer(PlanningUploadSerializer):
    rows = PlanningRowSerializer(many=True, read_only=True)
