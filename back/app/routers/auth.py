# app/routers/auth.py
from fastapi import APIRouter, Depends, HTTPException, Response, Request, status
from sqlalchemy.orm import Session
from jose import JWTError

from app.database import get_db
from app.services import auth_service
from app.schemas.auth_schema import LoginIn            # ✅ 요청 스키마 사용
from app.schemas.jsonapi import resource, single_doc
from app.config.settings import settings

router = APIRouter(tags=["auth"])  # ← prefix 없음 (패턴 B: main.py에서 /api/auth 부여)

# Refresh Token 쿠키 설정
COOKIE_NAME = "refresh_token"
COOKIE_PATH = f"{settings.API_PREFIX}/auth/refresh"   # 최종 경로 기준
COOKIE_SECURE = settings.env != "local"
COOKIE_SAMESITE = "Lax"   # 프론트/백 분리 도메인이면 "None" + Secure=True 권장

# 로그인 (Access + Refresh 발급)
@router.post("/login", status_code=status.HTTP_200_OK)
def login(data: LoginIn,                               # ✅ 명시적으로 LoginIn으로 검증
          response: Response,
          request: Request,
          db: Session = Depends(get_db)):
    try:
        ua = request.headers.get("user-agent")
        ip = request.client.host if request.client else None
        tokens = auth_service.login(db, data.user_id, data.password, user_agent=ua, ip=ip)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    # Refresh 쿠키 심기
    response.set_cookie(
        key=COOKIE_NAME,
        value=tokens.refresh_token,
        httponly=True,
        secure=COOKIE_SECURE,
        samesite=COOKIE_SAMESITE,
        max_age=60 * 60 * 24 * settings.refresh_token_expires_days,
        path=COOKIE_PATH,
    )

    # JSON:API 응답
    response.media_type = "application/vnd.api+json"
    doc = single_doc(
        resource("token", "access", {"access_token": tokens.access_token}),
        self_url=f"{settings.API_PREFIX}/auth/login",
    )
    return doc.model_dump()

# Access Token 갱신 (회전)
@router.post("/refresh", status_code=status.HTTP_200_OK)
def refresh(request: Request, response: Response, db: Session = Depends(get_db)):
    rt = request.cookies.get(COOKIE_NAME)
    if not rt:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing refresh token")

    try:
        new_access, new_refresh = auth_service.rotate_refresh_and_issue_access(db, rt)
    except (JWTError, ValueError):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired refresh token")

    # 새 refresh로 교체
    response.set_cookie(
        key=COOKIE_NAME,
        value=new_refresh,
        httponly=True,
        secure=COOKIE_SECURE,
        samesite=COOKIE_SAMESITE,
        max_age=60 * 60 * 24 * settings.refresh_token_expires_days,
        path=COOKIE_PATH,
    )

    response.media_type = "application/vnd.api+json"
    doc = single_doc(
        resource("token", "access", {"access_token": new_access}),
        self_url=f"{settings.API_PREFIX}/auth/refresh",
    )
    return doc.model_dump()

# 로그아웃 (Refresh 폐기 + 쿠키 삭제)
@router.post("/logout", status_code=status.HTTP_200_OK)
def logout(response: Response, request: Request, db: Session = Depends(get_db)):
    rt = request.cookies.get(COOKIE_NAME)
    if rt:
        auth_service.logout(db, rt)
    response.delete_cookie(COOKIE_NAME, path=COOKIE_PATH)

    response.media_type = "application/vnd.api+json"
    doc = single_doc(
        resource("result", "logout", {"detail": "logged out"}),
        self_url=f"{settings.API_PREFIX}/auth/logout",
    )
    return doc.model_dump()
