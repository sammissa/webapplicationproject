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
    """
    Custom log handler for storing log records in the database.

    This log handler extends the base DatabaseLogHandler to save log records into the
    CustomStatusLog model in the database. It overrides the `emit` method to handle log records
    and create corresponding CustomStatusLog objects.

    """

    def emit(self, record):
        """
        Emit a log record and save it in the database.

        Parameters:
            record (LogRecord): The log record to be saved.

        """
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
