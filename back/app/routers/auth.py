from fastapi import APIRouter, Depends, HTTPException, Response, Request
from sqlalchemy.orm import Session
from jose import JWTError
from app.services import auth_service
from app.database import get_db
from app.schemas.auth_schema import LoginIn, TokenOut
from app.config.settings import settings

# /auth 라우터 그룹 생성
router = APIRouter(prefix="/auth", tags=["auth"])

# Refresh Token 쿠키 설정 관련 상수
COOKIE_NAME = "refresh_token"                          # 쿠키 이름
COOKIE_PATH = f"{settings.API_PREFIX}/auth/refresh"    # refresh 엔드포인트에서만 전송
COOKIE_SECURE = settings.env != "local"                # 운영환경이면 secure=True (HTTPS 전용)
COOKIE_SAMESITE = "Lax"                                # SameSite 정책 (크로스 도메인이면 "None")

# 로그인 (Access + Refresh 발급)
@router.post("/login", response_model=TokenOut)
def login(
    data: LoginIn,                     # 요청 바디 (user_id, password)
    response: Response,                # 응답 객체 (쿠키 설정용)
    request: Request,                  # 요청 객체 (IP, User-Agent 확인용)
    db: Session = Depends(get_db),     # DB 세션 주입
):
    try:
        # 요청 헤더/클라이언트 정보 추출
        ua = request.headers.get("user-agent")
        ip = request.client.host if request.client else None

        # 사용자 검증 후 access/refresh 토큰 발급
        tokens = auth_service.login(
            db, data.user_id, data.password,
            user_agent=ua, ip=ip
        )
    except ValueError:
        # 아이디/비밀번호 불일치
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # ---- Refresh Token을 HttpOnly 쿠키에 저장 ----
    response.set_cookie(
        key=COOKIE_NAME,
        value=tokens.refresh_token,
        httponly=True,  # JS 접근 불가 (보안 강화)
        secure=COOKIE_SECURE,
        samesite=COOKIE_SAMESITE,
        max_age=60 * 60 * 24 * settings.refresh_token_expires_days,  # 유효기간
        path=COOKIE_PATH,  # refresh 요청에서만 전송되도록 제한
    )

    # 응답 JSON에는 Access Token만 포함
    return TokenOut(access_token=tokens.access_token)
# Access Token 갱신
@router.post("/refresh", response_model=TokenOut)
def refresh(request: Request, db: Session = Depends(get_db)):
    # 쿠키에서 refresh token 꺼내오기
    rt = request.cookies.get(COOKIE_NAME)
    if not rt:
        raise HTTPException(status_code=401, detail="Missing refresh token")
    try:
        # refresh token 검증 후 새 access token 발급
        new_access = auth_service.issue_access_only(db, rt)
        return TokenOut(access_token=new_access)
    except (JWTError, ValueError):
        # 토큰 손상/만료/폐기된 경우
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")


# 로그아웃 (Refresh 폐기 + 쿠키 삭제)
@router.post("/logout")
def logout(response: Response, request: Request, db: Session = Depends(get_db)):
    # 쿠키에 refresh token 있으면 DB에서 폐기 처리
    rt = request.cookies.get(COOKIE_NAME)
    if rt:
        auth_service.logout(db, rt)  # RefreshSession.revoked = True

    # 클라이언트 쿠키에서 refresh 삭제
    response.delete_cookie(COOKIE_NAME, path=COOKIE_PATH)
    return {"detail": "logged out"}
