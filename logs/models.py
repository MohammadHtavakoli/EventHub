from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _


class EventLog(models.Model):

    class Action(models.TextChoices):
        CREATE = 'CREATE', _('Create')
        UPDATE = 'UPDATE', _('Update')
        DELETE = 'DELETE', _('Delete')
        JOIN = 'JOIN', _('Join')
        LEAVE = 'LEAVE', _('Leave')
        STATUS_CHANGE = 'STATUS_CHANGE', _('Status Change')

    event = models.ForeignKey(
        'events.Event',
        on_delete=models.CASCADE,
        related_name='logs',
        null=True,
        blank=True
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='event_logs'
    )
    action = models.CharField(
        max_length=20,
        choices=Action.choices
    )
    description = models.TextField()
    metadata = models.JSONField(default=dict, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']
        verbose_name = _('event log')
        verbose_name_plural = _('event logs')

    def __str__(self):
        return f"{self.action} by {self.user.email} at {self.timestamp}"

