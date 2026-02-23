from rest_framework import permissions

class IsAdminUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'ADM'
    
class IsManagerUser(permissions.BasePermission):    
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'MNG'
    
class IsFactoryUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'FTR'