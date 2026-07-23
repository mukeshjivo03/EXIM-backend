# views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from .services.services import (
    get_all_accounts,
    get_account_closing_balances,
    get_account_ledger,
    get_accounts_summary,
    get_account_monthly_trend,
)
from accounts.permissions import HasAppPermission

VALID_BRANCHES = ('OIL', 'BEVERAGES' , 'MART')

def get_branch_or_error(request):
    branch = request.query_params.get('branch')
    if branch not in VALID_BRANCHES:
        return None, Response(
            {"error": "branch is required and must be one of: OIL, BEVERAGES"},
            status=status.HTTP_400_BAD_REQUEST
        )
    return branch, None


class AccountsView(APIView):
    def get_permissions(self):
            return [IsAuthenticated() , HasAppPermission('accounts.view_bank_accounts')]
        
        
    def get(self, request):
        branch, error = get_branch_or_error(request)
        if error:
            return error

        try:
            data = get_all_accounts(branch)
        except (ConnectionError, RuntimeError) as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_502_BAD_GATEWAY
            )

        return Response(data, status=status.HTTP_200_OK)


class AccountClosingBalanceView(APIView):
    def get_permissions(self):
        return [IsAuthenticated() , HasAppPermission('accounts.view_bank_closing')]
            
    

    def get(self, request):
        branch, error = get_branch_or_error(request)
        if error:
            return error

        acct_code = request.query_params.get('acct_code')
        from_date = request.query_params.get('from_date')
        to_date = request.query_params.get('to_date')
        if not acct_code or not from_date or not to_date:
            return Response(
                {"error": "acct_code, from_date and to_date are required (dates: YYYY-MM-DD)"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            data = get_account_closing_balances(branch, acct_code, from_date, to_date)
        except (ConnectionError, RuntimeError) as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_502_BAD_GATEWAY
            )

        return Response(data, status=status.HTTP_200_OK)


class AccountLedgerView(APIView):
    # def get_permissions(self):
        # return [IsAuthenticated() , HasAppPermission('accounts.view_bank_closing')]

    def get(self, request):
        branch, error = get_branch_or_error(request)
        if error:
            return error

        acct_code = request.query_params.get('acct_code')
        from_date = request.query_params.get('from_date')
        to_date = request.query_params.get('to_date')
        if not acct_code or not from_date or not to_date:
            return Response(
                {"error": "acct_code, from_date and to_date are required (dates: YYYY-MM-DD)"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            data = get_account_ledger(branch, acct_code, from_date, to_date)
        except (ConnectionError, RuntimeError) as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_502_BAD_GATEWAY
            )

        return Response(data, status=status.HTTP_200_OK)


class AccountsSummaryView(APIView):
    def get(self, request):
        branch, error = get_branch_or_error(request)
        if error:
            return error

        try:
            data = get_accounts_summary(branch)
        except (ConnectionError, RuntimeError) as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_502_BAD_GATEWAY
            )

        return Response(data, status=status.HTTP_200_OK)


class AccountMonthlyTrendView(APIView):
    def get(self, request):
        branch, error = get_branch_or_error(request)
        if error:
            return error

        acct_code = request.query_params.get('acct_code')
        from_date = request.query_params.get('from_date')
        to_date = request.query_params.get('to_date')
        if not acct_code or not from_date or not to_date:
            return Response(
                {"error": "acct_code, from_date and to_date are required (dates: YYYY-MM-DD)"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            data = get_account_monthly_trend(branch, acct_code, from_date, to_date)
        except (ConnectionError, RuntimeError) as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_502_BAD_GATEWAY
            )

        return Response(data, status=status.HTTP_200_OK)
