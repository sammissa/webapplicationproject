"""
References:
    Engineer and Ticket model were based on the code in the 'define models' section of Django tutorial:

    Visual Studio Code (no date) [online] Python and Django tutorial in Visual Studio Code. Available at:
    https://code.visualstudio.com/docs/python/tutorial-django (Accessed: 13 April 2022).
"""
from django.db import models
from django.utils.translation import gettext_lazy as _


class Engineer(models.Model):
    is_on_call = models.BooleanField(
        _('on call status'),
        default=False,
        help_text=_(
            'States if engineer is currently on call'
        ),
    )
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Ticket(models.Model):
    class Priority(models.TextChoices):
        LOW = 'L', 'Low'
        MED = 'M', 'Medium'
        HIGH = 'H', 'High'

    class Status(models.TextChoices):
        TD = 'TD', 'To do'
        IP = 'IP', 'In progress'
        D = 'D', 'Done'

    title = models.CharField(
        _('ticket title'),
        help_text=_(
            'Meaningful title of the ticket'
        ),
        max_length=300,
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
    description = models.CharField(
        _('ticket description'),
        default='',
        help_text=_(
            'Describes the issue and any action items an on-call engineer has reported'
        ),
        max_length=300
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
    reporter = models.ForeignKey(Engineer, on_delete=models.CASCADE, blank=True)
