from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = 'ADMIN', _('Admin')
        EVENT_CREATOR = 'EVENT_CREATOR', _('Event Creator')
        REGULAR_USER = 'REGULAR_USER', _('Regular User')

    email = models.EmailField(_('email address'), unique=True)
    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.REGULAR_USER,
    )

    # Add additional fields as needed
    bio = models.TextField(blank=True)

    # Make email the username field
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def __str__(self):
        return self.email

    @property
    def is_admin(self):
        return self.role == self.Role.ADMIN

    @property
    def is_event_creator(self):
        return self.role == self.Role.EVENT_CREATOR

    @property
    def is_regular_user(self):
        return self.role == self.Role.REGULAR_USER

