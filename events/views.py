from rest_framework import viewsets, status, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Count, F, Q
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from .models import Event, Participant
from .serializers import (
    EventSerializer, EventDetailSerializer,
    ParticipantSerializer, ParticipantCreateSerializer
)
from .permissions import IsEventCreatorOrReadOnly
from .filters import EventFilter
from users.permissions import IsAdminUser, IsEventCreator
from logs.models import EventLog


class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.annotate(
        participant_count=Count('participants')
    ).select_related('creator')
    serializer_class = EventSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = EventFilter
    search_fields = ['name', 'description', 'location']
    ordering_fields = ['date', 'created_at', 'name', 'participant_count']
    ordering = ['-date']

    def get_queryset(self):
        """
        Filter events based on user role and request parameters
        """
        queryset = super().get_queryset()

        # Filter by user's joined events
        joined = self.request.query_params.get('joined', None)
        if joined and self.request.user.is_authenticated:
            queryset = queryset.filter(participants__user=self.request.user)

        # Filter by user's created events
        created = self.request.query_params.get('created', None)
        if created and self.request.user.is_authenticated:
            queryset = queryset.filter(creator=self.request.user)

        # For non-authenticated users, only show open events
        if not self.request.user.is_authenticated:
            queryset = queryset.filter(status=Event.Status.OPEN)

        return queryset

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.action in ['create']:
            permission_classes = [IsEventCreator]
        elif self.action in ['update', 'partial_update', 'destroy']:
            permission_classes = [IsEventCreatorOrReadOnly]
        elif self.action in ['participants']:
            permission_classes = [permissions.IsAuthenticated, IsEventCreatorOrReadOnly]
        else:
            permission_classes = [permissions.AllowAny]
        return [permission() for permission in permission_classes]

    def get_serializer_class(self):
        """
        Return appropriate serializer class
        """
        if self.action == 'retrieve':
            return EventDetailSerializer
        return EventSerializer

    def perform_destroy(self, instance):
        """
        Check if event can be deleted
        """
        if not instance.can_be_deleted:
            return Response(
                {"detail": "Cannot delete an event with participants."},
                status=status.HTTP_400_BAD_REQUEST
            )
        instance.delete()

    @action(detail=True, methods=['get'])
    def participants(self, request, pk=None):
        """
        Get participants of an event
        """
        event = self.get_object()

        # Only event creator or admin can see participants
        if not (request.user == event.creator or request.user.is_admin):
            return Response(
                {"detail": "You do not have permission to view participants."},
                status=status.HTTP_403_FORBIDDEN
            )

        participants = event.participants.all()
        serializer = ParticipantSerializer(participants, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def join(self, request, pk=None):
        """
        Join an event
        """
        event = self.get_object()

        # Create serializer with event
        serializer = ParticipantCreateSerializer(
            data={'event': event.id},
            context={'request': request}
        )

        if serializer.is_valid():
            participant = serializer.save()

            # Log the event
            EventLog.objects.create(
                event=event,
                user=request.user,
                action='JOIN',
                description=f"User {request.user.email} joined event {event.name}"
            )

            return Response(
                ParticipantSerializer(participant).data,
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def leave(self, request, pk=None):
        """
        Leave an event
        """
        event = self.get_object()

        try:
            participant = Participant.objects.get(event=event, user=request.user)
        except Participant.DoesNotExist:
            return Response(
                {"detail": "You are not a participant of this event."},
                status=status.HTTP_400_BAD_REQUEST
            )

        participant.delete()

        # Log the event
        EventLog.objects.create(
            event=event,
            user=request.user,
            action='LEAVE',
            description=f"User {request.user.email} left event {event.name}"
        )

        return Response(status=status.HTTP_204_NO_CONTENT)


class ParticipantViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for Participant model (read-only)
    """
    serializer_class = ParticipantSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        Filter participants based on user role
        """
        user = self.request.user

        # Admin can see all participants
        if user.is_admin:
            return Participant.objects.all().select_related('user', 'event')

        # Event creators can see participants of their events
        if user.is_event_creator:
            return Participant.objects.filter(
                event__creator=user
            ).select_related('user', 'event')

        # Regular users can see their own participations
        return Participant.objects.filter(user=user).select_related('user', 'event')

