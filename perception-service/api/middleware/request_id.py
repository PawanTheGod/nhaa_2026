"""
Request ID & Timing Middleware for FastAPI Perception Service
==============================================================================
Generates unique X-Request-ID, tracks request execution duration, and logs
API metadata WITHOUT logging sensitive citizen text or audio contents.
==============================================================================
"""

import time
import uuid
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

class RequestIDMiddleware(BaseHTTPMiddleware):
    """
    Middleware injecting unique X-Request-ID and logging request execution metrics.
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        # Obtain or generate request ID
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        request.state.request_id = request_id

        start_time = time.time()
        
        # Execute request downstream
        response = await call_next(request)
        
        process_time = round(time.time() - start_time, 4)
        
        # Attach headers to response
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Process-Time"] = f"{process_time:.4f}s"

        # Privacy-preserving logging: log method, path, status, and duration (NO citizen text/audio logged)
        print(f"[API ACCESS LOG] RequestID={request_id} | Method={request.method} | Path={request.url.path} | Status={response.status_code} | Duration={process_time:.4f}s")

        return response
