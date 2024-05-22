import time
from datetime import datetime
from typing import Optional

from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse


class RateLimiter:
    def __init__(self, requests_per_minute: int = 60):
        self.requests_per_minute = requests_per_minute
        self._requests: dict[str, list[float]] = {}

    def _get_client_id(self, request: Request) -> str:
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        return request.client.host if request.client else "unknown"

    def _cleanup_old_requests(self, client_id: str, current_time: float):
        if client_id in self._requests:
            self._requests[client_id] = [
                t for t in self._requests[client_id]
                if current_time - t < 60
            ]

    def is_allowed(self, request: Request) -> bool:
        client_id = self._get_client_id(request)
        current_time = time.time()
        
        self._cleanup_old_requests(client_id, current_time)
        
        if client_id not in self._requests:
            self._requests[client_id] = []
        
        if len(self._requests[client_id]) >= self.requests_per_minute:
            return False
        
        self._requests[client_id].append(current_time)
        return True


rate_limiter = RateLimiter()


async def rate_limit_middleware(request: Request, call_next):
    if not rate_limiter.is_allowed(request):
        return JSONResponse(
            status_code=429,
            content={"error": "Too many requests", "code": "RATE_LIMIT_EXCEEDED"}
        )
    return await call_next(request)


async def request_logging_middleware(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    
    response.headers["X-Process-Time"] = str(process_time)
    return response
