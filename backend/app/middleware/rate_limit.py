import time
from collections import defaultdict

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

RATE_LIMITS = {
    "default": (100, 60),
    "auth": (10, 60),
    "post_create": (20, 60),
}

_ip_buckets: dict[str, list[float]] = defaultdict(list)
_last_cleanup = time.time()


def _client_ip(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


def _cleanup(now: float) -> None:
    global _last_cleanup
    if now - _last_cleanup < 60:
        return
    _last_cleanup = now
    cutoff = now - 120
    stale = [ip for ip, ts_list in _ip_buckets.items() if not ts_list or ts_list[-1] < cutoff]
    for ip in stale:
        del _ip_buckets[ip]


def _get_rate_limit_key(request: Request) -> tuple[str, int]:
    path = request.url.path
    method = request.method

    if path.startswith("/api/v1/auth/"):
        return "auth", RATE_LIMITS["auth"][0]
    if method == "POST" and path.startswith("/api/v1/posts") and not path.endswith(("/comments", "/likes", "/bookmarks", "/reports")):
        return "post_create", RATE_LIMITS["post_create"][0]
    return "default", RATE_LIMITS["default"][0]


class RateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if not request.url.path.startswith("/api/v1/"):
            return await call_next(request)

        ip = _client_ip(request)
        now = time.time()
        _cleanup(now)

        key, limit = _get_rate_limit_key(request)
        bucket_key = f"{ip}:{key}"
        bucket = _ip_buckets[bucket_key]

        window_start = now - RATE_LIMITS[key][1]
        bucket[:] = [t for t in bucket if t > window_start]

        if len(bucket) >= limit:
            return JSONResponse(
                status_code=429,
                content={
                    "detail": "Cok fazla istek gonderildi. Lutfen bir sure bekleyin.",
                    "retry_after": int(RATE_LIMITS[key][1] - (now - bucket[0])),
                },
            )

        bucket.append(now)
        response = await call_next(request)
        return response
