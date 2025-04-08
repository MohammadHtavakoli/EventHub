from django.contrib import admin
from .models import Event, Participant


class ParticipantInline(admin.TabularInline):
    model = Participant
    extra = 0
    readonly_fields = ('joined_at',)


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('name', 'date', 'location', 'status', 'creator', 'capacity', 'participant_count', 'created_at')
    list_filter = ('status', 'date', 'created_at')
    search_fields = ('name', 'description', 'location')
    readonly_fields = (
    'created_at', 'updated_at', 'participant_count', 'remaining_capacity', 'is_full', 'can_be_deleted')
    date_hierarchy = 'date'
    inlines = [ParticipantInline]

    fieldsets = (
        (None, {
            'fields': ('name', 'description', 'creator')
        }),
        ('Event Details', {
            'fields': ('date', 'location', 'capacity', 'status')
        }),
        ('Statistics', {
            'fields': ('participant_count', 'remaining_capacity', 'is_full', 'can_be_deleted')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def participant_count(self, obj):
        return obj.participant_count

    participant_count.short_description = 'Participants'

    def remaining_capacity(self, obj):
        return obj.remaining_capacity

    remaining_capacity.short_description = 'Remaining Capacity'

    def is_full(self, obj):
        return obj.is_full

    is_full.boolean = True
    is_full.short_description = 'Is Full'

    def can_be_deleted(self, obj):
        return obj.can_be_deleted

    can_be_deleted.boolean = True
    can_be_deleted.short_description = 'Can Be Deleted'


@admin.register(Participant)
class ParticipantAdmin(admin.ModelAdmin):
    list_display = ('user', 'event', 'joined_at')
    list_filter = ('joined_at', 'event__status')
    search_fields = ('user__email', 'user__username', 'event__name')
    readonly_fields = ('joined_at',)
    date_hierarchy = 'joined_at'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'event')

