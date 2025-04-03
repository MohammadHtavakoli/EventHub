from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Event, Participant

User = get_user_model()


class ParticipantSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source='user.email', read_only=True)
    user_name = serializers.SerializerMethodField()

    class Meta:
        model = Participant
        fields = ('id', 'user', 'user_email', 'user_name', 'joined_at')
        read_only_fields = ('joined_at',)

    def get_user_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}"


class EventSerializer(serializers.ModelSerializer):
    creator_name = serializers.SerializerMethodField()
    participant_count = serializers.IntegerField(read_only=True)
    remaining_capacity = serializers.IntegerField(read_only=True)
    is_full = serializers.BooleanField(read_only=True)
    can_be_deleted = serializers.BooleanField(read_only=True)

    class Meta:
        model = Event
        fields = (
            'id', 'name', 'description', 'capacity', 'date', 'location',
            'status', 'creator', 'creator_name', 'created_at', 'updated_at',
            'participant_count', 'remaining_capacity', 'is_full', 'can_be_deleted'
        )
        read_only_fields = ('creator', 'created_at', 'updated_at')

    def get_creator_name(self, obj):
        return f"{obj.creator.first_name} {obj.creator.last_name}"

    def create(self, validated_data):
        # Set the creator to the current user
        validated_data['creator'] = self.context['request'].user
        return super().create(validated_data)


class EventDetailSerializer(EventSerializer):
    participants = ParticipantSerializer(many=True, read_only=True, source='participants.all')

    class Meta(EventSerializer.Meta):
        fields = EventSerializer.Meta.fields + ('participants',)


class ParticipantCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Participant
        fields = ('event',)

    def validate_event(self, value):
        # Check if event is open
        if value.status != Event.Status.OPEN:
            raise serializers.ValidationError("Cannot join a closed or canceled event.")

        # Check if event has reached capacity
        if value.is_full:
            raise serializers.ValidationError("This event has reached its capacity.")

        # Check if user is already a participant
        user = self.context['request'].user
        if Participant.objects.filter(event=value, user=user).exists():
            raise serializers.ValidationError("You are already a participant of this event.")

        return value

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

