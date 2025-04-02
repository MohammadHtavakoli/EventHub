from rest_framework import serializers
from .models import Event, Participant, EventLog
from users.serializers import UserSerializer


class ParticipantSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Participant
        fields = ['id', 'user', 'joined_at']


class EventSerializer(serializers.ModelSerializer):
    creator = UserSerializer(read_only=True)
    current_participants = serializers.IntegerField(read_only=True)
    is_full = serializers.BooleanField(read_only=True)
    is_past = serializers.BooleanField(read_only=True)

    class Meta:
        model = Event
        fields = [
            'id', 'name', 'description', 'capacity', 'current_participants',
            'date', 'location', 'status', 'creator', 'created_at', 'updated_at',
            'is_full', 'is_past'
        ]
        read_only_fields = ['id', 'creator', 'created_at', 'updated_at']

    def create(self, validated_data):
        validated_data['creator'] = self.context['request'].user
        return super().create(validated_data)


class EventLogSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = EventLog
        fields = ['id', 'event', 'user', 'action', 'details', 'timestamp']
        read_only_fields = fields