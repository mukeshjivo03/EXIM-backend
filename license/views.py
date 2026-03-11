from django.shortcuts import render
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .models import AdvanceLicenseHeaders, AdvanceLicenseLines
from .serializers import AdvanceLicenseHeaderSerialzer, AdvanceLicenseLineSerialzer
from accounts.permissions import IsAdminUser, IsManagerUser


# Create your views here.
class AdvanceLicenseHeadersListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated, IsAdminUser | IsManagerUser]
    queryset = AdvanceLicenseHeaders.objects.all()
    serializer_class = AdvanceLicenseHeaderSerialzer


class AdvanceLicenseLinesListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated, IsAdminUser | IsManagerUser]
    queryset = AdvanceLicenseLines.objects.all()
    serializer_class = AdvanceLicenseLineSerialzer


class AdvanceLicenseRetrieveDeleteView(generics.RetrieveDestroyAPIView):
    permission_classes = [IsAuthenticated, IsAdminUser | IsManagerUser]
    queryset = AdvanceLicenseHeaders.objects.all()
    serializer_class = AdvanceLicenseHeaderSerialzer
    lookup_field = 'license_no'
    


    