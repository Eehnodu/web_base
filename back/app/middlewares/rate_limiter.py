from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address

# .env 인코딩 이슈 회피: .env를 읽지 않도록 우회(또는 ASCII-only 별도 파일)
limiter = Limiter(
    key_func=get_remote_address,
    headers_enabled=True,
    default_limits=["100/minute"],  # 필요에 맞게 조정
    config_filename="rate.env",     # 존재하지 않아도 OK(있다면 ASCII만)
)

# 예외 핸들러는 함수 레벨로(uvicorn --reload 시 중복 정의 방지)
async def _rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(status_code=429, content={"detail": "Rate limit exceeded"})

def add_rate_limiter(app: FastAPI):
    # Limiter 인스턴스를 앱 상태에 연결
    app.state.limiter = limiter

    # ★ Flask식 init_app 대신, 미들웨어를 추가
    app.add_middleware(SlowAPIMiddleware)

    # ★ 예외 핸들러 등록
    app.add_exception_handler(RateLimitExceeded, _rate_limit_handler)
