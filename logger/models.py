from django.contrib.admin.models import LogEntry
from django.db import models
from django.utils.translation import gettext_lazy as _
from django_db_logger.models import StatusLog


class CustomStatusLog(StatusLog):
    username = models.CharField(max_length=150)

    class Meta:
        app_label = 'logger'
        ordering = ('-create_datetime',)
        verbose_name = _("user log entry")
        verbose_name_plural = _("user log entries")


class CustomLogEntry(LogEntry):
    class Meta:
        proxy = True
        app_label = 'logger'
        verbose_name = _("admin log entry")
        verbose_name_plural = _("admin log entries")
        ordering = ["-action_time"]
