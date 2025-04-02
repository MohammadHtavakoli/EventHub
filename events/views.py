from django.db import transaction
from django.db.models import Q, Count
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import generics, permissions, status, filters
from rest_framework.response import Response
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from .models import Event, Participant, EventLog
from .serializers import EventSerializer, ParticipantSerializer, EventLogSerializer
from .permissions import IsEventCreatorOrReadOnly, IsEventCreator, IsAdminOrCreator


class EventListCreateView(generics.ListCreateAPIView):
    serializer_class = EventSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status']
    search_fields = ['name', 'description', 'location']
    ordering_fields = ['date', 'created_at', 'name']
    ordering = ['date']

    def get_permissions(self):
        if self.request.method == 'POST':
            return [permissions.IsAuthenticated(), IsAdminOrCreator()]
        return [permissions.AllowAny()]

    def get_queryset(self):
        queryset = Event.objects.annotate(
            participant_count=Count('participants')
        )

        # Filter by date
        date_filter = self.request.query_params.get('date')
        if date_filter:
            try:
                filter_date = timezone.datetime.fromisoformat(date_filter.replace('Z', '+00:00'))
                queryset = queryset.filter(date__gte=filter_date)
            except ValueError:
                pass

        # Filter by available capacity
        capacity_filter = self.request.query_params.get('capacity')
        if capacity_filter and capacity_filter.lower() == 'true':
            queryset = queryset.filter(participant_count__lt=models.F('capacity'))

        return queryset

    def perform_create(self, serializer):
        # Check if user has reached the limit of open events
        if self.request.user.role != 'admin':
            open_events_count = Event.objects.filter(
                creator=self.request.user,
                status='open'
            ).count()

            # Limit to 5 open events for non-admin users
            if open_events_count >= 5:
                return Response(
                    {"detail": "You have reached the maximum number of open events."},
                    status=status.HTTP_400_BAD_REQUEST
                )

        with transaction.atomic():
            event = serializer.save(creator=self.request.user)

            # Create log entry
            EventLog.objects.create(
                event=event,
                user=self.request.user,
                action='create',
                details={'event_id': event.id, 'event_name': event.name}
            )


class EventDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [IsEventCreatorOrReadOnly]

    def perform_update(self, serializer):
        with transaction.atomic():
            event = serializer.save()

            # Create log entry
            EventLog.objects.create(
                event=event,
                user=self.request.user,
                action='update',
                details={
                    'event_id': event.id,
                    'event_name': event.name,
                    'updated_fields': list(serializer.validated_data.keys())
                }
            )

    def destroy(self, request, *args, **kwargs):
        event = self.get_object()

        # Check if event has participants
        if event.participants.exists():
            return Response(
                {"detail": "Cannot delete an event with participants."},
                status=status.HTTP_400_BAD_REQUEST
            )

        with transaction.atomic():
            # Store event details for logging
            event_details = {
                'event_id': event.id,
                'event_name': event.name
            }

            # Delete the event
            event.delete()

            # Create log entry
            EventLog.objects.create(
                event=None,  # Event is deleted
                user=request.user,
                action='delete',
                details=event_details
            )

            return Response(status=status.HTTP_204_NO_CONTENT)


class EventParticipantsView(generics.ListAPIView):
    serializer_class = ParticipantSerializer
    permission_classes = [permissions.IsAuthenticated, IsEventCreator]

    def get_queryset(self):
        event = get_object_or_404(Event, pk=self.kwargs['pk'])
        self.check_object_permissions(self.request, event)
        return Participant.objects.filter(event=event)


class JoinEventView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        event = get_object_or_404(Event, pk=pk)

        # Check if event is open
        if event.status != 'open':
            return Response(
                {"detail": "Event is not open for registration."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check if event is full
        if event.is_full:
            return Response(
                {"detail": "Event has reached its capacity."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check if user is already a participant
        if Participant.objects.filter(event=event, user=request.user).exists():
            return Response(
                {"detail": "You are already registered for this event."},
                status=status.HTTP_400_BAD_REQUEST
            )

        with transaction.atomic():
            # Create participant
            participant = Participant.objects.create(
                event=event,
                user=request.user
            )

            # Create log entry
            EventLog.objects.create(
                event=event,
                user=request.user,
                action='join',
                details={
                    'event_id': event.id,
                    'event_name': event.name,
                    'participant_id': participant.id
                }
            )

            return Response(
                {"detail": "Successfully joined the event."},
                status=status.HTTP_201_CREATED
            )


class LeaveEventView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        event = get_object_or_404(Event, pk=pk)

        # Check if user is a participant
        participant = get_object_or_404(Participant, event=event, user=request.user)

        with transaction.atomic():
            # Store participant details for logging
            participant_details = {
                'event_id': event.id,
                'event_name': event.name,
                'participant_id': participant.id
            }

            # Delete participant
            participant.delete()

            # Create log entry
            EventLog.objects.create(
                event=event,
                user=request.user,
                action='leave',
                details=participant_details
            )

            return Response(
                {"detail": "Successfully left the event."},
                status=status.HTTP_200_OK
            )


class EventLogsView(generics.ListAPIView):
    serializer_class = EventLogSerializer
    permission_classes = [permissions.IsAuthenticated, IsEventCreator]

    def get_queryset(self):
        event = get_object_or_404(Event, pk=self.kwargs['pk'])
        self.check_object_permissions(self.request, event)
        return EventLog.objects.filter(event=event)


class AdminEventLogsView(generics.ListAPIView):
    serializer_class = EventLogSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_permissions(self):
        if not self.request.user.is_authenticated:
            return [permissions.IsAuthenticated()]
        if self.request.user.role != 'admin':
            return [permissions.IsAdminUser()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        return EventLog.objects.all()