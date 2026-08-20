import logging
import traceback

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

logger = logging.getLogger("meridyen.errors")


class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
            return await call_next(request)
        except Exception:
            request_id = getattr(request.state, "request_id", "unknown")
            logger.error(
                "Hatali istek [%s] %s %s:\n%s",
                request_id,
                request.method,
                request.url.path,
                traceback.format_exc(),
            )
            return JSONResponse(
                status_code=500,
                content={
                    "detail": "Sunucuda beklenmeyen bir hata olustu.",
                    "request_id": request_id,
                },
            )
