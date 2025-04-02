from rest_framework import generics, permissions
from rest_framework.response import Response
from events.models import Event, Participant
from events.serializers import EventSerializer


class UserEventsView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = EventSerializer

    def get(self, request, *args, **kwargs):
        # Get events created by the user
        created_events = Event.objects.filter(creator=request.user)
        created_serializer = EventSerializer(created_events, many=True)

        # Get events joined by the user
        joined_event_ids = Participant.objects.filter(user=request.user).values_list('event_id', flat=True)
        joined_events = Event.objects.filter(id__in=joined_event_ids)
        joined_serializer = EventSerializer(joined_events, many=True)

        return Response({
            'created': created_serializer.data,
            'joined': joined_serializer.data
        })