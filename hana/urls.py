from django.urls import path
from .views import (
    AccountsView,
    AccountClosingBalanceView,
    AccountLedgerView,
    AccountsSummaryView,
    AccountMonthlyTrendView,
)


urlpatterns = [
    path('accounts/', AccountsView.as_view()),
    path('accounts/summary/', AccountsSummaryView.as_view()),
    path('accounts/closing-balances/', AccountClosingBalanceView.as_view()),
    path('accounts/ledger/', AccountLedgerView.as_view()),
    path('accounts/monthly-trend/', AccountMonthlyTrendView.as_view()),
]
