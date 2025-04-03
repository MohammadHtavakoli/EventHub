from rest_framework import permissions

class IsAdminUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_admin

class IsEventCreator(permissions.BasePermission):

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and (
            request.user.is_event_creator or request.user.is_admin
        )

class IsSelfOrAdmin(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user and request.user.is_authenticated and (
            obj.id == request.user.id or request.user.is_admin
        )

