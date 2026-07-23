from django.urls import path
from .views import AccountsView, AccountClosingBalanceView


urlpatterns = [
    path('accounts/', AccountsView.as_view()),
    path('accounts/closing-balances/', AccountClosingBalanceView.as_view()),
]
