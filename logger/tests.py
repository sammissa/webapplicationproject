import logging

from django.contrib import admin
from django.contrib.admin import AdminSite
from django.contrib.auth.models import Group
from django.test import TestCase, RequestFactory
from django.contrib.admin.models import LogEntry
from django_db_logger.models import StatusLog

from logger.admin import LogEntryAdmin, CustomStatusLogAdmin
from logger.db_log_handler import CustomDatabaseLogHandler
from logger.models import CustomStatusLog, CustomLogEntry


class CustomStatusLogTestCase(TestCase):
    def test_model_fields(self):
        fields = CustomStatusLog._meta.fields
        field_names = [field.name for field in fields]
        self.assertIn('username', field_names)

    def test_model_meta_options(self):
        self.assertEqual(CustomStatusLog._meta.app_label, 'logger')
        self.assertEqual(CustomStatusLog._meta.ordering, ('-create_datetime',))
        self.assertEqual(CustomStatusLog._meta.verbose_name, 'user log entry')
        self.assertEqual(CustomStatusLog._meta.verbose_name_plural, 'user log entries')


class CustomLogEntryTestCase(TestCase):
    def test_model_meta_options(self):
        self.assertTrue(CustomLogEntry._meta.proxy)
        self.assertEqual(CustomLogEntry._meta.app_label, 'logger')
        self.assertEqual(CustomLogEntry._meta.verbose_name, 'admin log entry')
        self.assertEqual(CustomLogEntry._meta.verbose_name_plural, 'admin log entries')
        self.assertEqual(CustomLogEntry._meta.ordering, ['-action_time'])


class LogEntryTestCase(TestCase):
    def test_model_proxy(self):
        self.assertTrue(issubclass(CustomLogEntry, LogEntry))
        self.assertFalse(issubclass(LogEntry, CustomLogEntry))


class CustomDatabaseLogHandlerTestCase(TestCase):
    def test_emit(self):
        handler = CustomDatabaseLogHandler()
        logger = logging.getLogger('custom_logger')
        logger.addHandler(handler)

        logger.error('Test log message', extra={'username': 'testuser'})

        log_entry = CustomStatusLog.objects.first()
        self.assertIsNotNone(log_entry)
        self.assertEqual(log_entry.logger_name, 'custom_logger')
        self.assertEqual(log_entry.level, logging.ERROR)
        self.assertEqual(log_entry.msg, 'Test log message')
        self.assertIsNone(log_entry.trace)
        self.assertEqual(log_entry.username, 'testuser')


class CustomStatusLogAdminTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.admin_site = AdminSite()
        self.admin = CustomStatusLogAdmin(CustomStatusLog, self.admin_site)

    def test_list_display_links(self):
        self.assertEqual(self.admin.list_display_links, ('colored_msg', 'create_datetime_format'))

    def test_list_display(self):
        self.assertEqual(self.admin.list_display, ('create_datetime_format', 'username', 'colored_msg', 'traceback'))

    def test_list_filter(self):
        self.assertEqual(self.admin.list_filter, ('level', 'username'))

    def test_search_fields(self):
        self.assertEqual(self.admin.search_fields, ('username', 'colored_msg', 'traceback'))

    def test_has_add_permission(self):
        request = self.factory.get('/admin/logger/customstatuslog/add/')
        self.assertFalse(self.admin.has_add_permission(request))

    def test_has_change_permission(self):
        request = self.factory.get('/admin/logger/customstatuslog/1/change/')
        self.assertFalse(self.admin.has_change_permission(request))

    def test_has_delete_permission(self):
        request = self.factory.get('/admin/logger/customstatuslog/1/delete/')
        self.assertFalse(self.admin.has_delete_permission(request))


class LogEntryAdminTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.admin_site = AdminSite()
        self.admin = LogEntryAdmin(CustomLogEntry, self.admin_site)

    def test_date_hierarchy(self):
        self.assertEqual(self.admin.date_hierarchy, 'action_time')

    def test_list_display(self):
        self.assertEqual(self.admin.list_display, ('action_time', 'user', 'content_type', 'object_repr', 'action_flag'))

    def test_list_filter(self):
        self.assertEqual(self.admin.list_filter, ('action_flag', 'user', 'content_type'))

    def test_search_fields(self):
        self.assertEqual(self.admin.search_fields, ('object_repr', 'change_message'))

    def test_has_add_permission(self):
        request = self.factory.get('/admin/logger/customlogentry/add/')
        self.assertFalse(self.admin.has_add_permission(request))

    def test_has_change_permission(self):
        request = self.factory.get('/admin/logger/customlogentry/1/change/')
        self.assertFalse(self.admin.has_change_permission(request))

    def test_has_delete_permission(self):
        request = self.factory.get('/admin/logger/customlogentry/1/delete/')
        self.assertFalse(self.admin.has_delete_permission(request))


class AdminSiteTestCase(TestCase):
    def test_unregister(self):
        self.assertNotIn(StatusLog, admin.site._registry)
        self.assertNotIn(Group, admin.site._registry)
