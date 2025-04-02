from rest_framework import permissions


class IsEventCreatorOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the creator of the event
        return obj.creator == request.user


class IsEventCreator(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # Permissions are only allowed to the creator of the event
        return obj.creator == request.user


class IsAdminOrCreator(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and (
                request.user.role == 'admin' or request.user.role == 'creator'
        )