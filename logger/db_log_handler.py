"""
References:
    CustomerDatabaseLogHandler is based on 'DatabaseLogHandler' class and following 'Build your own database logger'
    instructions from the django-db-logger package found at:

    CiCiUi (2023) [online] django-db-logger.
    Available at: https://github.com/CiCiUi/django-db-logger (Accessed: 29 June 2023).
"""
import logging

from django_db_logger.db_log_handler import DatabaseLogHandler

db_default_formatter = logging.Formatter()


class CustomDatabaseLogHandler(DatabaseLogHandler):
    def emit(self, record):
        from .models import CustomStatusLog
        
        trace = None

        if record.exc_info:
            trace = db_default_formatter.formatException(record.exc_info)

        msg = record.getMessage()

        if hasattr(record, 'username'):
            username = record.username
        else:
            username = ''

        kwargs = {
            'logger_name': record.name,
            'level': record.levelno,
            'msg': msg,
            'trace': trace,
            'username': username
        }

        CustomStatusLog.objects.create(**kwargs)
