from rest_framework import serializers
from .models import EventLog


class EventLogSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source='user.email', read_only=True)
    event_name = serializers.CharField(source='event.name', read_only=True)

    class Meta:
        model = EventLog
        fields = (
            'id', 'event', 'event_name', 'user', 'user_email',
            'action', 'description', 'metadata', 'timestamp'
        )
        read_only_fields = ('id', 'timestamp')

