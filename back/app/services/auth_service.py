from datetime import datetime, timedelta, timezone
from uuid import uuid4
import hashlib
from jose import jwt, JWTError
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from app.repository import auth_repo
from app.config.settings import settings
from app.schemas.auth_schema import TokenOut

# 비밀번호 해싱/검증용 bcrypt 컨텍스트
pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Password hashing helpers
def hash_password(plain: str) -> str:
    """
    입력받은 평문 비밀번호를 bcrypt로 해싱해서 반환
    - 회원가입 시 DB에 저장할 때 사용
    """
    return pwd.hash(plain)

def verify_password(plain: str, hashed: str) -> bool:
    """
    평문 비밀번호와 DB에 저장된 bcrypt 해시를 비교 검증
    - 로그인 시 인증에 사용
    """
    return pwd.verify(plain, hashed)

# Token helpers
def _sha256_hex(s: str) -> str:
    """
    문자열을 SHA-256으로 해시 후 16진수 문자열 반환
    - refresh token 원문을 그대로 DB에 저장하지 않고
      해시값만 저장하여 보안 강화 (토큰 유출 방지)
    """
    return hashlib.sha256(s.encode("utf-8")).hexdigest()

def _create_token(sub: str, typ: str, exp: timedelta, jti: str | None = None) -> str:
    """
    JWT 토큰 생성 함수
    - sub: 사용자 식별자 (user_id)
    - typ: access 또는 refresh 구분
    - exp: 만료 시간 (timedelta)
    - jti: refresh token 고유 ID (회전 관리용)
    """
    now = datetime.now(timezone.utc)
    payload = {
        "sub": sub,                        # 사용자 ID
        "type": typ,                       # access / refresh
        "iat": int(now.timestamp()),       # 발급 시간
        "exp": int((now + exp).timestamp()), # 만료 시간
        "jti": jti or str(uuid4()),        # 토큰 식별자(Refresh 관리에 필요)
    }
    return jwt.encode(payload, settings.secret_key, algorithm=settings.jwt_algorithm)

def _decode_token(token: str) -> dict:
    """
    JWT 토큰 해석 (검증 포함)
    - 시크릿 키와 알고리즘으로 서명 검증 후 payload 반환
    - 검증 실패 시 jose.JWTError 예외 발생
    """
    return jwt.decode(token, settings.secret_key, algorithms=[settings.jwt_algorithm])

# Auth flows
def login(db: Session, user_id: str, password: str, *, user_agent: str | None = None, ip: str | None = None) -> TokenOut:
    """
    로그인 처리
    1. 아이디/비밀번호 확인
    2. access token 발급
    3. refresh token 발급 및 DB 저장 (hash 형태)
    4. access/refresh 토큰 반환
    """
    # 사용자 조회
    user = auth_repo.get_by_user_id(db, user_id)
    if not user or not verify_password(password, user.user_password):
        raise ValueError("invalid credentials")

    # ---- access token 발급 ----
    access = _create_token(
        sub=str(user.id), typ="access",
        exp=timedelta(minutes=settings.access_token_expires_minutes),
    )

    # ---- refresh token 발급 ----
    refresh_exp = timedelta(days=settings.refresh_token_expires_days)
    jti = str(uuid4())  # refresh 식별자
    refresh = _create_token(
        sub=str(user.id), typ="refresh",
        exp=refresh_exp, jti=jti,
    )

    # refresh 토큰은 DB에 해시로만 저장 (보안)
    auth_repo.create_refresh_session(
        db,
        user_id=user.id,
        jti=jti,
        token_hash=_sha256_hex(refresh),
        expires_at=datetime.now(timezone.utc) + refresh_exp,
        user_agent=user_agent,
        ip=ip,
    )

    # 반환: access_token + refresh_token
    return TokenOut(access_token=access, refresh_token=refresh)

def issue_access_only(db: Session, refresh_token: str) -> str:
    """
    refresh token을 검증 후 새 access token만 발급
    (refresh token rotation은 하지 않음)
    """
    # 토큰 파싱
    payload = _decode_token(refresh_token)
    if payload.get("type") != "refresh":
        raise ValueError("invalid token type")

    jti = payload.get("jti")
    uid = payload.get("sub")

    # DB에 저장된 refresh 세션 조회
    rs = auth_repo.get_refresh_session_by_jti(db, jti)
    if not rs or rs.revoked:
        raise ValueError("refresh revoked or not found")

    # 평문 refresh 토큰이 DB의 해시와 일치하는지 검증
    if rs.token_hash != _sha256_hex(refresh_token):
        raise ValueError("token hash mismatch")

    # 만료 여부 확인
    now = datetime.now(timezone.utc)
    if rs.expires_at <= now:
        raise ValueError("refresh expired")

    # 마지막 사용 시각 업데이트
    auth_repo.touch_refresh_last_used(db, jti)

    # 새로운 access token 발급
    return _create_token(
        sub=str(uid), typ="access",
        exp=timedelta(minutes=settings.access_token_expires_minutes),
    )

def logout(db: Session, refresh_token: str) -> None:
    """
    로그아웃 처리
    - refresh token을 DB에서 'revoked' 상태로 변경
    - 이후 같은 refresh token 재사용 불가
    """
    try:
        payload = _decode_token(refresh_token)
        jti = payload.get("jti")
        auth_repo.mark_refresh_revoked(db, jti)
    except JWTError:
        # 이미 만료되었거나 손상된 토큰이면 무시 (쿠키만 지우면 됨)
        pass
