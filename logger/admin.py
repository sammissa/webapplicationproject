"""
References:
    CustomStatusLogAdmin is based on 'StatusLogAdmin' model and following 'Build your own database logger' instructions
    from the django-db-logger package found at:

    CiCiUi (2023) [online] django-db-logger.
    Available at: https://github.com/CiCiUi/django-db-logger (Accessed: 29 June 2023).

    LogEntryAdmin is based on 'Register Django’s LogEntry model in Django Admin' section found at:

    Albeik, M. (2020) [online] Monitoring user actions with LogEntry in Django Admin, Medium. Available at:
    https://medium.datadriveninvestor.com/monitoring-user-actions-with-logentry-in-django-admin-8c9fbaa3f442
    (Accessed: 29 June 2023).
"""
from __future__ import unicode_literals

from django.contrib import admin
from django.contrib.auth.models import Group
from django_db_logger.admin import StatusLogAdmin
from django_db_logger.models import StatusLog

from .models import CustomStatusLog, CustomLogEntry


@admin.register(CustomStatusLog)
class CustomStatusLogAdmin(StatusLogAdmin):
    list_display_links = ('colored_msg', 'create_datetime_format',)
    list_display = ('create_datetime_format', 'username', 'colored_msg', 'traceback')
    list_filter = ('level', 'username')
    search_fields = ('username', 'colored_msg', 'traceback')

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(CustomLogEntry)
class LogEntryAdmin(admin.ModelAdmin):
    date_hierarchy = 'action_time'
    list_display = ('action_time', 'user', 'content_type', 'object_repr', 'action_flag')
    list_filter = ('action_flag', 'user', 'content_type')
    search_fields = ('object_repr', 'change_message')

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


admin.site.unregister(StatusLog)
admin.site.unregister(Group)
