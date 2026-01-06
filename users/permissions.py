from rest_framework import permissions


class Admin(permissions.BasePermission):
    """Allow access for admins"""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_admin

class Owner(permissions.BasePermission):
    """Allow access for owners"""
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_authenticated and request.user.is_owner

class Tenant(permissions.BasePermission):
    """Allow access for tenants"""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_tenant

class AdminOrOwner(permissions.BasePermission):
    """Allow access for admins or owers"""
    def has_object_permission(self, request, view, obj):
        if request.user.is_admin:
            return True
        if hasattr(obj, 'owner'):
            return obj.owner == request.user
        if hasattr(obj, 'user'):
            return obj.user == request.user
        return obj == request.user

class OwnerOrUserReadOnly(permissions.BasePermission):
    """Allow read access for everyone, changes access only for owbers"""
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        if hasattr(obj, 'owner'):
            return obj.owner == request.user
        if hasattr(obj, 'author'):
            return obj.author == request.user
        if hasattr(obj, 'user'):
            return obj.user == request.user
        return False