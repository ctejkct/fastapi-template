"""Request context middleware for logging correlation ids."""

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from app.core.logging import generate_request_id, set_request_context


class RequestContextMiddleware(BaseHTTPMiddleware):
    """Attach request ids to log context and response headers."""

    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get("X-Request-ID") or generate_request_id()
        trace_id = request.headers.get("X-Trace-ID") or generate_request_id()
        set_request_context(request_id=request_id, trace_id=trace_id)

        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response
