from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import Logout , RegisterView , GetDeleteUpdate, ListUservView , MyTokenObtainPairView

urlpatterns = [
    path('login/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('login/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('logout/', Logout.as_view(), name='logout'),
    path('register/', RegisterView.as_view(), name='register'),

    path('users/', ListUservView.as_view(), name='delete_user'),
    path('user/<int:id>/', GetDeleteUpdate.as_view(), name='delete_or_get_user'),

]