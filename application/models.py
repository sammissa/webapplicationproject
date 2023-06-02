"""
References:
    EngineerUser and Ticket model were based on the code in the 'define models' section of Django tutorial:

    Visual Studio Code (no date) [online] Python and Django tutorial in Visual Studio Code. Available at:
    https://code.visualstudio.com/docs/python/tutorial-django (Accessed: 13 April 2022).
"""
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class EngineerUser(AbstractUser):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    is_on_call = models.BooleanField(
        _('on call status'),
        default=False,
        help_text=_(
            'States if engineer is currently on call'
        ),
    )

    REQUIRED_FIELDS = ["email", "first_name", "last_name"]

    def __str__(self):
        return self.get_full_name()


class Ticket(models.Model):
    class Priority(models.TextChoices):
        LOW = 'L', _('Low')
        MED = 'M', _('Medium')
        HIGH = 'H', _('High')

    class Status(models.TextChoices):
        TD = 'TD', _('To do')
        IP = 'IP', _('In progress')
        D = 'D', _('Done')

    title = models.CharField(
        _('ticket title'),
        help_text=_(
            'Meaningful title of the ticket'
        ),
        max_length=100,
        unique=True,
    )
    created = models.DateTimeField('date created')
    priority = models.CharField(
        _('ticket priority'),
        choices=Priority.choices,
        default=Priority.LOW,
        help_text=_(
            'Describes the importance of the ticket, L = Low, M = Medium, H = High'
        ),
        max_length=50
    )
    description = models.TextField(
        _('ticket description'),
        default='',
        help_text=_(
            'Describes the issue and any action items an on-call engineer has reported'
        ),
        max_length=1000
    )
    status = models.CharField(
        _('ticket status'),
        choices=Status.choices,
        default=Status.TD,
        help_text=_(
            'Describes the current state of the ticket. TD = To do, IP = In progress, D = Done'
        ),
        max_length=50
    )
    reporter = models.ForeignKey(EngineerUser, on_delete=models.CASCADE, blank=True)
