import logging
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request, FastAPI
from time import time

logger = logging.getLogger("uvicorn.access")

class AccessLogMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time()
        response = await call_next(request)
        duration = round((time() - start_time) * 1000)
        client_ip = request.client.host
        method = request.method
        path = request.url.path
        status = response.status_code

        logger.info(f"{client_ip} {method} {path} - {status} - {duration}ms")
        return response

def add_access_log(app: FastAPI):
    app.add_middleware(AccessLogMiddleware)
