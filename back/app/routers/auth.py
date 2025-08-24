from fastapi import APIRouter, Depends, HTTPException, Response, Request
from sqlalchemy.orm import Session
from jose import JWTError
from app.services import auth_service
from app.database import get_db
from app.schemas.auth_schema import LoginIn, TokenOut
from app.config.settings import settings

router = APIRouter(prefix="/auth", tags=["auth"])

COOKIE_NAME = "refresh_token"
COOKIE_PATH = f"{settings.API_PREFIX}/auth/refresh"
COOKIE_SECURE = settings.env != "local"   # 로컬 http면 False
COOKIE_SAMESITE = "Lax"                   # 크로스도메인이면 "None"

@router.post("/login", response_model=TokenOut)
def login(data: LoginIn, response: Response, request: Request, db: Session = Depends(get_db)):
    try:
        ua = request.headers.get("user-agent")
        ip = request.client.host if request.client else None
        tokens = auth_service.login(db, data.user_id, data.password, user_agent=ua, ip=ip)
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # refresh 쿠키 심기
    response.set_cookie(
        key=COOKIE_NAME,
        value=tokens.refresh_token,
        httponly=True,
        secure=COOKIE_SECURE,
        samesite=COOKIE_SAMESITE,
        max_age=60 * 60 * 24 * settings.refresh_token_expires_days,
        path=COOKIE_PATH,
    )
    # 응답 바디에는 access만
    return TokenOut(access_token=tokens.access_token)

@router.post("/refresh", response_model=TokenOut)
def refresh(request: Request, db: Session = Depends(get_db)):
    rt = request.cookies.get(COOKIE_NAME)
    if not rt:
        raise HTTPException(status_code=401, detail="Missing refresh token")
    try:
        new_access = auth_service.issue_access_only(db, rt)
        return TokenOut(access_token=new_access)
    except (JWTError, ValueError):
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")

@router.post("/logout")
def logout(response: Response, request: Request, db: Session = Depends(get_db)):
    rt = request.cookies.get(COOKIE_NAME)
    if rt:
        auth_service.logout(db, rt)  # DB에서 즉시 폐기
    response.delete_cookie(COOKIE_NAME, path=COOKIE_PATH)
    return {"detail": "logged out"}
