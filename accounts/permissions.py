from rest_framework.permissions import BasePermission

class IsSuperUser(BasePermission):
    """ This will check wheather user has is_superuser permission or not"""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_superuser