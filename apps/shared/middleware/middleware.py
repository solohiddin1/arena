import datetime
import logging
import logging.handlers
import os
from threading import Lock

from django.urls import reverse
from django.contrib.auth.hashers import check_password
from django.utils.deprecation import MiddlewareMixin
from django.conf import settings

from arena.settings import BASE_DIR

LOG_DIR = os.path.join(BASE_DIR, "logs")
os.makedirs(LOG_DIR, exist_ok=True)

# Thread-safe singleton logger
_logger = None
_logger_lock = Lock()
_current_log_file = None


def get_log_file():
    today = datetime.date.today().strftime("%Y-%m-%d")
    return os.path.join(LOG_DIR, f"{today}.log")


def get_logger():
    global _logger, _current_log_file

    current_log_file = get_log_file()

    with _logger_lock:
        if _logger is None or _current_log_file != current_log_file:
            if _logger is not None:
                for handler in _logger.handlers[:]:
                    handler.close()
                    _logger.removeHandler(handler)

            _logger = logging.getLogger("daily_logger")
            _logger.setLevel(logging.INFO)
            _logger.handlers.clear()
            _logger.propagate = False

            handler = logging.handlers.RotatingFileHandler(
                current_log_file,
                maxBytes=50 * 1024 * 1024,
                backupCount=5,
                encoding='utf-8'
            )
            formatter = logging.Formatter("[{asctime}] {levelname} {message}", style="{")
            handler.setFormatter(formatter)
            _logger.addHandler(handler)

            _current_log_file = current_log_file

    return _logger


def is_swagger_request(path: str) -> bool:
    return any([
        path.startswith("/swagger"),
        path.startswith("/redoc"),
        path.startswith("/openapi"),
    ])


def should_skip_logging(path: str) -> bool:
    return any([
        path.startswith("/swagger"),
        path.startswith("/redoc"),
        path.startswith("/api/media/"),
        path.startswith("/api/static/"),
        path.startswith("/favicon.ico"),    
    ])


class ExceptionMiddleware(MiddlewareMixin):

    def process_exception(self, request, exception):
        if is_swagger_request(request.path):
            return None

        logger = get_logger()
        logger.exception(exception)
        return None


class RequestResponseLoggingMiddleware(MiddlewareMixin):

    MAX_LOG_LENGTH = 500  # limit logged content size

    def process_request(self, request):
        if should_skip_logging(request.path):
            return None

        logger = get_logger()
        try:
            body = request.body.decode(errors="ignore")
        except Exception:
            body = "<unreadable body>"

        if len(body) > self.MAX_LOG_LENGTH:
            body = body[:self.MAX_LOG_LENGTH] + "... [truncated]"

        logger.info(
            f"REQUEST | {request.method} {request.get_full_path()} | Body: {body}"
        )

    def process_response(self, request, response):
        if should_skip_logging(request.path):
            return response

        logger = get_logger()

        # Skip logging binary responses (images, pdfs, etc.)
        content_type = response.get("Content-Type", "")
        if any(ct in content_type for ct in ["image", "pdf", "octet-stream"]):
            content = f"<binary content skipped: {content_type}>"
        else:
            try:
                content = response.content.decode(errors="ignore")
            except Exception:
                content = "<unreadable content>"

            if len(content) > self.MAX_LOG_LENGTH:
                content = content[:self.MAX_LOG_LENGTH] + "... [truncated]"

        logger.info(
            f"RESPONSE | {request.method} {request.get_full_path()} | "
            f"Status: {response.status_code} | Content: {content}"
        )
        return response
