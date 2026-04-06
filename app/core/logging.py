"""Logging configuration with request-scoped context support."""

import contextvars
import logging
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

from pythonjsonlogger import jsonlogger

from app.config.settings import get_settings

request_id_ctx: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar(
    "request_id", default=None
)
trace_id_ctx: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar("trace_id", default=None)
user_id_ctx: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar("user_id", default=None)


def set_request_context(
    request_id: Optional[str] = None,
    trace_id: Optional[str] = None,
    user_id: Optional[str] = None,
) -> None:
    """Attach request identifiers to the current context."""
    if request_id:
        request_id_ctx.set(request_id)
    if trace_id:
        trace_id_ctx.set(trace_id)
    if user_id:
        user_id_ctx.set(user_id)


def generate_request_id() -> str:
    """Generate a short request id."""
    return str(uuid.uuid4())[:8]


class ProductionJsonFormatter(jsonlogger.JsonFormatter):
    """JSON formatter enriched with service metadata."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        kwargs.setdefault("json_indent", None)
        super().__init__(*args, **kwargs)
        self.settings = get_settings()

    def add_fields(
        self,
        log_record: Dict[str, Any],
        record: logging.LogRecord,
        message_dict: Dict[str, Any],
    ) -> None:
        super().add_fields(log_record, record, message_dict)
        log_record["timestamp"] = datetime.now(timezone.utc).isoformat()
        log_record["level"] = record.levelname
        log_record["logger"] = record.name
        log_record["service"] = self.settings.app_name
        log_record["version"] = self.settings.app_version
        log_record["environment"] = self.settings.environment.value

        if request_id_ctx.get():
            log_record["request_id"] = request_id_ctx.get()
        if trace_id_ctx.get():
            log_record["trace_id"] = trace_id_ctx.get()
        if user_id_ctx.get():
            log_record["user_id"] = user_id_ctx.get()

        log_record["file"] = record.filename
        log_record["line"] = record.lineno
        log_record["function"] = record.funcName

        if record.exc_info:
            log_record["exception"] = self.formatException(record.exc_info)


def setup_logging(log_level: Optional[str] = None, json_format: Optional[bool] = None) -> None:
    """Configure application logging."""
    settings = get_settings()
    level = log_level or settings.log_level
    use_json = json_format if json_format is not None else settings.log_json_format

    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)

    if use_json:
        console_handler.setFormatter(ProductionJsonFormatter())
    else:
        console_handler.setFormatter(logging.Formatter("%(levelname)-5s | %(name)s | %(message)s"))

    root_logger.addHandler(console_handler)

    if not use_json:
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        file_handler = logging.FileHandler(log_dir / "app.log")
        file_handler.setLevel(level)
        file_handler.setFormatter(ProductionJsonFormatter())
        root_logger.addHandler(file_handler)

    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.error").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("redis").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """Get a named logger."""
    return logging.getLogger(name)
