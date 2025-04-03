import django_filters
from django.utils import timezone
from .models import Event


class EventFilter(django_filters.FilterSet):
    date_from = django_filters.DateTimeFilter(field_name='date', lookup_expr='gte')
    date_to = django_filters.DateTimeFilter(field_name='date', lookup_expr='lte')
    status = django_filters.ChoiceFilter(choices=Event.Status.choices)
    min_capacity = django_filters.NumberFilter(method='filter_min_capacity')
    max_capacity = django_filters.NumberFilter(method='filter_max_capacity')
    has_capacity = django_filters.BooleanFilter(method='filter_has_capacity')
    upcoming = django_filters.BooleanFilter(method='filter_upcoming')

    class Meta:
        model = Event
        fields = ['status', 'creator', 'date_from', 'date_to']

    # Filter events with at least the specified remaining capacity
    def filter_min_capacity(self, queryset, name, value):
        return queryset.filter(capacity__gte=value)

    # Filter events with at least the specified remaining capacity
    def filter_max_capacity(self, queryset, name, value):
        return queryset.filter(capacity__lte=value)

    # Filter events that have remaining capacity
    def filter_has_capacity(self, queryset, name, value):
        from django.db.models import Count, F

        queryset = queryset.annotate(
            participant_count=Count('participants')
        )

        if value:  # Has capacity
            return queryset.filter(participant_count__lt=F('capacity'))
        else:  # No capacity
            return queryset.filter(participant_count__gte=F('capacity'))

    # Filter upcoming events
    def filter_upcoming(self, queryset, name, value):
        now = timezone.now()

        if value:  # Upcoming events
            return queryset.filter(date__gte=now)
        else:  # Past events
            return queryset.filter(date__lt=now)

