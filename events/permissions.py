from rest_framework import permissions

# Permission to only allow event creators to edit their events
class IsEventCreatorOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the event creator or admin
        return request.user and request.user.is_authenticated and (
                obj.creator == request.user or request.user.is_admin
        )

# Permission to only allow users to manage their own participation
class IsParticipantUser(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # Only allow users to manage their own participation
        return request.user and request.user.is_authenticated and (
                obj.user == request.user or request.user.is_admin
        )

