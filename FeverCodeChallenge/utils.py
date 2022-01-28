import logging
import os
import traceback
import datetime
from django.conf import settings
from django.utils import timezone
from rest_framework.exceptions import ValidationError
from staticdata.models import Log


LOG_FORMAT = '%(asctime)s :: %(levelname)8s :: %(filename)16s:%(lineno)3s :: %(message)s'
LOG_DATE_FORMAT = '%d/%m/%Y %H:%M:%S'
LOG_MAX_BYTES = 10 * 1024 * 1024
LOG_BACKUP_COUNT = 1000


def get_logger(appName='Console', toConsole=True, toFile=True, logLevel=logging.INFO, extra_handler=None, dbLogLevel=logging.INFO):
    """Instantiates and returns a logger. Can log to console, filename or both"""

    logger = logging.getLogger(appName)

    logger.setLevel(logLevel)

    if extra_handler is not None and not any([isinstance(handler, type(extra_handler)) for handler in logger.handlers]):
        logger.addHandler(extra_handler)

    if toConsole and not any([isinstance(handler, logging.StreamHandler) for handler in logger.handlers]):
        logger.addHandler(get_console_handler())

    if toFile and not any([isinstance(handler, logging.handlers.RotatingFileHandler) for handler in logger.handlers]):
        logger.addHandler(get_file_handler(appName))

    if not any([isinstance(handler, DBLoggerHandler) for handler in logger.handlers]):
        logger.addHandler(DBLoggerHandler(appName=appName, level=dbLogLevel))

    return logger


def get_console_handler():
    """Instantiates and returns a console handler"""

    handler = logging.StreamHandler()
    # set level to DEBUG if Django is set to debug mode, INFO otherwise
    if settings.DEBUG:
        handler.setLevel(logging.DEBUG)
    else:
        handler.setLevel(logging.INFO)

    # Adjust line format for the log, including fixed width columns
    fmt = logging.Formatter(LOG_FORMAT, datefmt=LOG_DATE_FORMAT)
    handler.setFormatter(fmt)

    return handler


def get_file_handler(appName):
    """Instantiates and returns a file handler, requires the name of the application, which will be used for the log folder"""

    # Create filehandler to write to the file LOG_ROOT/%appName%/YYYYMMDD.log (LOG_ROOT usually will be be DJANGO_ROOT/logs)
    if not os.path.isdir(settings.LOG_ROOT):
        os.mkdir(settings.LOG_ROOT)

    logDir = os.path.join(settings.LOG_ROOT, appName)
    if not os.path.isdir(logDir):
        os.mkdir(logDir)

    filepath = os.path.join(logDir, timezone.now().strftime("%Y%m%d.log"))
    handler = logging.handlers.RotatingFileHandler(filepath, maxBytes=LOG_MAX_BYTES, backupCount=LOG_BACKUP_COUNT)

    fmt = logging.Formatter(LOG_FORMAT, datefmt=LOG_DATE_FORMAT)
    handler.setFormatter(fmt)

    # set level to DEBUG if Django is set to debug mode, INFO otherwise
    if settings.DEBUG:
        handler.setLevel(logging.DEBUG)
    else:
        handler.setLevel(logging.INFO)

    return handler


class DBLoggerHandler(logging.Handler):
    def __init__(self, level=logging.NOTSET, appName=''):
        logging.Handler.__init__(self, level=level)
        self.app_name = appName

    def emit(self, record):
        # General log info
        log_text = str(record.getMessage())

        # Exception data logging
        if record.exc_info:
            exc_type, exc_value, exc_traceback = record.exc_info
            if exc_traceback:
                log_text += ":\n"
                for l in traceback.format_exception(exc_type, exc_value, exc_traceback):
                    if isinstance(l, str):
                        log_text += l
                    else:
                        log_text += str(l, "utf-8", errors='replace')

        Log.objects.create(level=record.levelno, application=self.app_name, text=log_text)

    def handleError(self, record):
        # General log info
        log_text = "Error while saving to database"
        message = record.getMessage()
        if isinstance(message, str):
            log_text = message
        else:
            log_text = str(message, "utf-8", errors='replace')

        Log.objects.create(level=logging.ERROR, application=self.app_name, text=log_text)


def api_validate(request, param, param_type='date', code=1, default=None, null=False):
    try:
        response = request.query_params or request.POST
        result = None
        if param not in response:
            if not null:
                raise ValidationError({'error': 'Missing %s parameter.' % param})
            return default
        if param_type == 'date':
            result = datetime.datetime.strptime(response.get(param), '%Y-%m-%d').date()
        return result
    except Exception:
        raise ValidationError({"error": {"code": code, "message": 'wrong format of param %s' % param}, "data": None})
