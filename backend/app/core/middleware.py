import uuid
import time
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response


class RequestIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        request.state.request_id = request_id
        start_time = time.perf_counter()

        response: Response = await call_next(request)

        process_time = time.perf_counter() - start_time
        duration_ms = process_time * 1000
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Process-Time"] = f"{process_time:.4f}"

        try:
            from app.adapters.system_monitor_adapter import record_request_latency
            record_request_latency(duration_ms)
        except Exception:
            pass

        return response