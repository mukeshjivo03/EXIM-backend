from django.urls import path

from .views import (
    PlanningUploadListCreateView,
    PlanningUploadDetailView,
    PlanningLatestView,
)

urlpatterns = [
    path('uploads/', PlanningUploadListCreateView.as_view()),
    path('uploads/<int:pk>/', PlanningUploadDetailView.as_view()),
    path('latest/', PlanningLatestView.as_view()),
]
