from django.contrib import admin
from .models import Event, Participant, EventLog


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('name', 'date', 'location', 'status', 'capacity', 'current_participants', 'creator')
    list_filter = ('status', 'date')
    search_fields = ('name', 'description', 'location')
    date_hierarchy = 'date'


@admin.register(Participant)
class ParticipantAdmin(admin.ModelAdmin):
    list_display = ('user', 'event', 'joined_at')
    list_filter = ('joined_at',)
    search_fields = ('user__name', 'user__email', 'event__name')


@admin.register(EventLog)
class EventLogAdmin(admin.ModelAdmin):
    list_display = ('action', 'event', 'user', 'timestamp')
    list_filter = ('action', 'timestamp')
    search_fields = ('event__name', 'user__name', 'user__email')