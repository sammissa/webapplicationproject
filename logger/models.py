"""
References:
    CustomStatusLog is based on 'StatusLog' model and following 'Build your own database logger' instructions from the
    django-db-logger package found at:

    CiCiUi (2023) [online] django-db-logger.
    Available at: https://github.com/CiCiUi/django-db-logger (Accessed: 29 June 2023).

    CustomLogEntry is based on the 'Recent Django versions require to create a proxy for LogEntry' Stack Overflow
    comment found at:

    Straninger, A. (2015) [online] ‘Answer to “django - Joining LogEntry to actual models”’, Stack Overflow.
    Available at: https://stackoverflow.com/a/28793145 (Accessed: 29 June 2023).
"""
from django.contrib.admin.models import LogEntry
from django.db import models
from django.utils.translation import gettext_lazy as _
from django_db_logger.models import StatusLog


class CustomStatusLog(StatusLog):
    """
    Custom model for storing user log entries.

    This model extends the base StatusLog model to add an additional 'username' field.
    It represents log entries related to user activity and provides options for custom ordering.

    Attributes:
        username (str): The username associated with the log entry.

    Meta:
        app_label (str): The label of the application this model belongs to.
        ordering (list): The default sorting order of log entries based on 'create_datetime'.
        verbose_name (str): The human-readable name for a single log entry.
        verbose_name_plural (str): The human-readable name for multiple log entries.

    """

    username = models.CharField(max_length=150)

    class Meta:
        app_label = 'logger'
        ordering = ('-create_datetime',)
        verbose_name = _("user log entry")
        verbose_name_plural = _("user log entries")


class CustomLogEntry(LogEntry):
    """
    Custom proxy model for displaying admin log entries.

    This model serves as a proxy for the base LogEntry model, allowing customization
    of its display options. It represents log entries related to administrative actions.

    Meta:
        proxy (bool): Indicates that this model is a proxy for the base LogEntry model.
        app_label (str): The label of the application this model belongs to.
        verbose_name (str): The human-readable name for a single log entry.
        verbose_name_plural (str): The human-readable name for multiple log entries.
        ordering (list): The default sorting order of log entries based on 'action_time'.

    """

    class Meta:
        proxy = True
        app_label = 'logger'
        verbose_name = _("admin log entry")
        verbose_name_plural = _("admin log entries")
        ordering = ["-action_time"]
