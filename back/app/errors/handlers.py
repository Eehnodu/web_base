# app/errors/handlers.py
from fastapi import FastAPI, Request, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from app.errors.problem_details import problem
from app.errors import codes  # 상태코드 상수 정의

def register_error_handlers(app: FastAPI) -> None:
    # 422 Validation Error
    @app.exception_handler(RequestValidationError)
    async def handle_422(request: Request, exc: RequestValidationError):
        return JSONResponse(
            status_code=codes.HTTP_422_UNPROCESSABLE_ENTITY,
            content=problem(
                status=codes.HTTP_422_UNPROCESSABLE_ENTITY,
                title="Validation error",
                detail=str(exc.errors()),
                instance=str(request.url.path)
            ),
            media_type="application/problem+json"
        )

    # 일반적인 HTTPException
    @app.exception_handler(HTTPException)
    async def handle_http_exc(request: Request, exc: HTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content=problem(
                status=exc.status_code,
                title="HTTP Error",
                detail=str(exc.detail),
                instance=str(request.url.path)
            ),
            media_type="application/problem+json"
        )

    # 500 Internal Server Error
    @app.middleware("http")
    async def catch_all(request: Request, call_next):
        try:
            return await call_next(request)
        except HTTPException:
            raise
        except Exception:
            return JSONResponse(
                status_code=codes.HTTP_500_INTERNAL_SERVER_ERROR,
                content=problem(
                    status=codes.HTTP_500_INTERNAL_SERVER_ERROR,
                    title="Internal Server Error",
                    detail="Unexpected error occurred",
                    instance=str(request.url.path)
                ),
                media_type="application/problem+json"
            )
