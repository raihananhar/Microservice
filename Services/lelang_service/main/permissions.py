from rest_framework.permissions import BasePermission


class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        # Check if user is authenticated
        if not request.user.is_authenticated:
            return False
        # Allow access only if the user has admin or partner role
        return request.user.role == 'ADMIN'


class IsPartner(BasePermission):
    def has_permission(self, request, view):
        # Check if user is authenticated
        if not request.user.is_authenticated:
            return False
        # Allow access only if the user has admin or partner role
        return request.user.role == 'PARTNER'


class IsUser(BasePermission):
    def has_permission(self, request, view):
        # Check if user is authenticated
        if not request.user.is_authenticated:
            return False
        # Allow access only if the user has admin or partner role
        return request.user.role == 'USER'


class IsPartnerOrUser(BasePermission):
    def has_permission(self, request, view):
        # Check if user is authenticated
        if not request.user.is_authenticated:
            return False
        # Allow access only if the user has admin or partner role
        return request.user.role in ['USER', 'PARTNER']