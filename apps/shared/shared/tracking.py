import contextvars
import uuid

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

# Context variable to store request ID
request_id_ctx = contextvars.ContextVar("request_id", default=None)


def generate_request_id():
    return f"REQ-{uuid.uuid4().hex[:12].upper()}"


def get_request_id():
    return request_id_ctx.get()


class RequestTrackingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get("X-Request-ID") or generate_request_id()
        token = request_id_ctx.set(request_id)
        try:
            response = await call_next(request)
            response.headers["X-Request-ID"] = request_id
            return response
        finally:
            request_id_ctx.reset(token)
