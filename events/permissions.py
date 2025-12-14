from rest_framework import permissions

class IsOrganizerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow organizers to edit objects.
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_authenticated and request.user.is_organizer()

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        # Write permissions are only allowed to the organizer of the event
        # Use hasattr to check if obj is Event or related
        if hasattr(obj, 'organizer'):
            return obj.organizer == request.user
        if hasattr(obj, 'event'):
            return obj.event.organizer == request.user
        return False
