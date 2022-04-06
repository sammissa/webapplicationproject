import django.contrib.auth.models
from django.db import models
from django.contrib import admin
from django.contrib.auth.models import User

from django.utils import timezone


class Engineer(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Ticket(models.Model):
    SEVERITY = (
        (1, "LOW"),
        (2, "MEDIUM"),
        (3, "HIGH")
    )
    title = models.CharField(max_length=300)
    created = models.DateTimeField("date created")
    severity = models.IntegerField(default=1, choices=SEVERITY)
    reporter = models.ForeignKey(User, on_delete=models.CASCADE, blank=True)

    def __str__(self):
        """Returns a string representation of a message."""
        date = timezone.localtime(self.created)
        return f"'{self.title}' created on {date.strftime('%A, %d %B, %Y at %X')} with severity of '{self.severity}'"

