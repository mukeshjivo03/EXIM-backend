from django.urls import path
from .views import fetchEximRatesView

urlpatterns = [
    path('fetch/', fetchEximRatesView.as_view(), name='fetch-exim-rates'),
]

