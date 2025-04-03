from rest_framework import viewsets, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import EventLog
from .serializers import EventLogSerializer
from users.permissions import IsAdminUser


class EventLogViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = EventLogSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['event', 'user', 'action']
    ordering_fields = ['timestamp']
    ordering = ['-timestamp']

    # Only admins can see all logs
    # Event creators can see logs for their events
    def get_permissions(self):
        return [permissions.IsAuthenticated()]

    # Filter logs based on user role
    def get_queryset(self):

        user = self.request.user

        # Admin can see all logs
        if user.is_admin:
            return EventLog.objects.all().select_related('user', 'event')

        # Event creators can see logs for their events
        if user.is_event_creator:
            return EventLog.objects.filter(
                event__creator=user
            ).select_related('user', 'event')

        # Regular users can see logs for events they participate in
        return EventLog.objects.filter(
            event__participants__user=user
        ).select_related('user', 'event')

