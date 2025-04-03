from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.db.models import Count


class Event(models.Model):
    class Status(models.TextChoices):
        OPEN = 'OPEN', _('Open')
        CLOSED = 'CLOSED', _('Closed')
        CANCELED = 'CANCELED', _('Canceled')

    name = models.CharField(max_length=255)
    description = models.TextField()
    capacity = models.PositiveIntegerField(default=settings.EVENT_MANAGEMENT.get('DEFAULT_EVENT_CAPACITY', 50))
    date = models.DateTimeField()
    location = models.CharField(max_length=255)
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.OPEN,
    )
    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='created_events'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date']
        verbose_name = _('event')
        verbose_name_plural = _('events')

    def __str__(self):
        return self.name

    def clean(self):
        # Check if user has reached the maximum number of open events
        if self.status == self.Status.OPEN and not self.pk:  # Only for new events
            user_open_events_count = Event.objects.filter(
                creator=self.creator,
                status=self.Status.OPEN
            ).count()

            max_open_events = settings.EVENT_MANAGEMENT.get('MAX_OPEN_EVENTS_PER_USER', 5)
            if user_open_events_count >= max_open_events:
                raise ValidationError(
                    _('You have reached the maximum number of open events (%(max_events)s).'),
                    params={'max_events': max_open_events},
                )

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    @property
    def participant_count(self):
        return self.participants.count()

    @property
    def is_full(self):
        return self.participant_count >= self.capacity

    @property
    def remaining_capacity(self):
        return max(0, self.capacity - self.participant_count)

    @property
    def can_be_deleted(self):
        return self.participant_count == 0


class Participant(models.Model):
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name='participants'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='participations'
    )
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('event', 'user')
        verbose_name = _('participant')
        verbose_name_plural = _('participants')

    def __str__(self):
        return f"{self.user.email} - {self.event.name}"

    def clean(self):
        # Check if event is open
        if self.event.status != Event.Status.OPEN:
            raise ValidationError(_('Cannot join a closed or canceled event.'))

        # Check if event has reached capacity
        if self.event.is_full and not self.pk:  # Only for new participants
            raise ValidationError(_('This event has reached its capacity.'))

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

