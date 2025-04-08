from django.contrib import admin
from .models import EventLog


@admin.register(EventLog)
class EventLogAdmin(admin.ModelAdmin):
    list_display = ('action', 'event', 'user', 'timestamp')
    list_filter = ('action', 'timestamp')
    search_fields = ('event__name', 'user__email', 'description')
    readonly_fields = ('event', 'user', 'action', 'description', 'metadata', 'timestamp')
    date_hierarchy = 'timestamp'

    fieldsets = (
        (None, {
            'fields': ('action', 'event', 'user')
        }),
        ('Details', {
            'fields': ('description', 'metadata')
        }),
        ('Timestamp', {
            'fields': ('timestamp',)
        }),
    )

    def has_add_permission(self, request):
        # Logs should only be created programmatically
        return False

    def has_change_permission(self, request, obj=None):
        # Logs should not be editable
        return False

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'event')

