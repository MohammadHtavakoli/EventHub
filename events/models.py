from django.db import models
from django.conf import settings
from django.utils import timezone


class Event(models.Model):
    STATUS_CHOICES = (
        ('open', 'Open'),
        ('closed', 'Closed'),
        ('canceled', 'Canceled'),
    )

    name = models.CharField(max_length=255)
    description = models.TextField()
    capacity = models.PositiveIntegerField()
    date = models.DateTimeField()
    location = models.CharField(max_length=255)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='open')
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='created_events')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return self.name

    @property
    def current_participants(self):
        return self.participants.count()

    @property
    def is_full(self):
        return self.current_participants >= self.capacity

    @property
    def is_past(self):
        return self.date < timezone.now()


class Participant(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='participants')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='participating_events')
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-joined_at']
        unique_together = ['event', 'user']

    def __str__(self):
        return f"{self.user.name} - {self.event.name}"


class EventLog(models.Model):
    ACTION_CHOICES = (
        ('create', 'Create'),
        ('update', 'Update'),
        ('delete', 'Delete'),
        ('join', 'Join'),
        ('leave', 'Leave'),
    )

    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='logs', null=True, blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='event_logs')
    action = models.CharField(max_length=10, choices=ACTION_CHOICES)
    details = models.JSONField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.action} - {self.event.name if self.event else 'Deleted Event'} by {self.user.name if self.user else 'Unknown'}"