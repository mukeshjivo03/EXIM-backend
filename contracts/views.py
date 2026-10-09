from rest_framework import generics
from datetime import date
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q

from .serializers import DomesticReportSerializer , ContractSerializer , LoadingSerializer, FreightSerializer , ContractDropdownSerializer , DomesticContractDetailSerializer
from .models import DomesticReports , DomesticContractDetails
from accounts.permissions import HasAppPermission
from rest_framework.parsers import MultiPartParser, FormParser
from .services import DCImportError, import_dc_workbook


class DomesticContractDetailListView(APIView):
    """DC workbook rows, newest invoice first.

    ?year=2026 narrows to that financial year (1 Apr - 31 Mar); omit for all rows.
    Filtering and paging beyond this are done client-side, as on the other list pages.
    """

    def get_permissions(self):
        return [IsAuthenticated(), HasAppPermission('contracts.view_domesticcontractdetails')]

    def get(self, request):
        data = DomesticContractDetails.objects.all()

        year = request.query_params.get('year')
        if year:
            try:
                fy = int(year)
            except ValueError:
                return Response({'detail': f"Invalid year: {year!r}"}, status=400)
            data = data.filter(invoice_date__range=[date(fy, 4, 1), date(fy + 1, 3, 31)])

        serializer = DomesticContractDetailSerializer(data, many=True)
        return Response(serializer.data)


MAX_DC_UPLOAD_BYTES = 10 * 1024 * 1024


def _flag(request, name):
    return str(request.data.get(name, '')).lower() in ('1', 'true', 'yes', 'on')


class DomesticContractDetailUploadView(APIView):
    """Upload the DC workbook and upsert it on invoice number.

    multipart: file (.xlsx), dry_run (check only, write nothing), keep_partial
    (import rows with unreadable optional cells, leaving those columns empty).
    Returns counts plus the rows skipped / flagged / failed. If any row can't be
    parsed nothing is written (400 with the same report).
    """
    parser_classes = [MultiPartParser, FormParser]

    def get_permissions(self):
        # An upsert both creates and updates rows.
        return [
            IsAuthenticated(),
            HasAppPermission('contracts.add_domesticcontractdetails'),
            HasAppPermission('contracts.change_domesticcontractdetails'),
        ]

    def post(self, request):
        upload = request.FILES.get('file')
        if not upload:
            return Response({'detail': 'Choose the DC Excel file to upload.'}, status=400)
        if not upload.name.lower().endswith(('.xlsx', '.xlsm')):
            return Response({'detail': 'Please upload an .xlsx DC workbook.'}, status=400)
        if upload.size > MAX_DC_UPLOAD_BYTES:
            return Response({'detail': 'That file is larger than the 10 MB limit.'}, status=400)

        try:
            result = import_dc_workbook(
                upload,
                upload.name,
                dry_run=_flag(request, 'dry_run'),
                keep_partial=_flag(request, 'keep_partial'),
            )
        except DCImportError as exc:
            return Response({'detail': str(exc)}, status=400)

        body = result.as_dict()
        if result.errors:
            body['detail'] = f"{len(result.errors)} row(s) could not be read, so nothing was imported."
            return Response(body, status=400)
        return Response(body)


class DomesticReportListView(APIView):
    def get_permissions(self):
        return [IsAuthenticated() , HasAppPermission('contracts.view_domesticreports')]
    def get(self,request):
        year = request.query_params.get('year')
        user_year = int(year)
        
        # start_date = date(user_year , 4 , 1)
        
        start_date = date(user_year , 2 , 1)
        end_date = date(user_year+ 1 , 3 , 31)
        print(start_date , end_date)
        
        # data = DomesticReports.objects.filter(grpo_date__range=[start_date , end_date])
        data = DomesticReports.objects.filter( po_date__range=[start_date, end_date]).order_by('-po_date')

        serializer = DomesticReportSerializer(data , many=True)
        return Response(serializer.data)
        
        

class ContractPostView(generics.CreateAPIView):
    def get_permissions(self):
        return [IsAuthenticated() , HasAppPermission('contracts.add_domesticreports')]

    queryset = DomesticReports.objects.all()
    serializer_class = ContractSerializer   
    
class LoadingPostView(generics.UpdateAPIView):
    def get_permissions(self):
        return [IsAuthenticated() , HasAppPermission('contracts.change_domesticreports')]

    queryset = DomesticReports.objects.all()
    serializer_class = LoadingSerializer
    lookup_field = 'id'
    
class FrieghtPostView(generics.UpdateAPIView):
    def get_permissions(self):
        return [IsAuthenticated() , HasAppPermission('contracts.change_domesticreports')]
    
    queryset = DomesticReports.objects.all()
    serializer_class = FreightSerializer
    lookup_field = 'id'
    
class ContractGetView(generics.RetrieveUpdateDestroyAPIView):

    def get_permissions(self):
        if self.request.method == 'DELETE':
            return [IsAuthenticated() , HasAppPermission('contracts.delete_domesticreports')]
        if self.request.method in ['PUT' , 'PATCH']:
            return [IsAuthenticated(), HasAppPermission('contracts.change_domesticreports')] 

        return [IsAuthenticated(), HasAppPermission('contracts.view_domesticreports')]

    
    queryset = DomesticReports.objects.all()
    serializer_class = DomesticReportSerializer
    lookup_field = 'id'

class ContractDropdownView(generics.ListAPIView):
    def get_permissions(self):
        return [IsAuthenticated(), HasAppPermission('contracts.view_domesticreports')]
    
    queryset = DomesticReports.objects.all().order_by('-created_at')
    serializer_class = ContractDropdownSerializer
    


    