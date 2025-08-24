from datetime import datetime, timedelta, timezone
from uuid import uuid4
import hashlib
from jose import jwt, JWTError
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from app.repository import auth_repo
from app.config.settings import settings
from app.schemas.auth_schema import TokenOut

pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ----- Password hashing -----
def hash_password(plain: str) -> str:
    return pwd.hash(plain)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd.verify(plain, hashed)

# ----- Token helpers -----
def _sha256_hex(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()

def _create_token(sub: str, typ: str, exp: timedelta, jti: str | None = None) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": sub,
        "type": typ,
        "iat": int(now.timestamp()),
        "exp": int((now + exp).timestamp()),
        "jti": jti or str(uuid4()),
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.jwt_algorithm)

def _decode_token(token: str) -> dict:
    return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.jwt_algorithm])

# ----- Auth flows -----
def login(db: Session, user_id: str, password: str, *, user_agent: str | None = None, ip: str | None = None) -> TokenOut:
    user = auth_repo.get_by_user_id(db, user_id)
    if not user or not verify_password(password, user.user_password):
        raise ValueError("invalid credentials")

    # access
    access = _create_token(
        sub=str(user.id), typ="access",
        exp=timedelta(minutes=settings.access_token_expires_minutes),
    )

    # refresh (with jti) + DB 저장(해시)
    refresh_exp = timedelta(days=settings.refresh_token_expires_days)
    jti = str(uuid4())
    refresh = _create_token(
        sub=str(user.id), typ="refresh",
        exp=refresh_exp, jti=jti,
    )
    auth_repo.create_refresh_session(
        db,
        user_id=user.id,
        jti=jti,
        token_hash=_sha256_hex(refresh),
        expires_at=datetime.now(timezone.utc) + refresh_exp,
        user_agent=user_agent,
        ip=ip,
    )
    return TokenOut(access_token=access, refresh_token=refresh)

def issue_access_only(db: Session, refresh_token: str) -> str:
    payload = _decode_token(refresh_token)
    if payload.get("type") != "refresh":
        raise ValueError("invalid token type")

    jti = payload.get("jti")
    uid = payload.get("sub")

    rs = auth_repo.get_refresh_session_by_jti(db, jti)
    if not rs or rs.revoked:
        raise ValueError("refresh revoked or not found")

    # 토큰 평문이 DB의 해시와 일치하는지 검증 (유출/재사용 방지)
    if rs.token_hash != _sha256_hex(refresh_token):
        raise ValueError("token hash mismatch")

    # 만료 체크
    now = datetime.now(timezone.utc)
    if rs.expires_at <= now:
        raise ValueError("refresh expired")

    # 사용 흔적 업데이트
    auth_repo.touch_refresh_last_used(db, jti)

    # 새 access만 발급(회전 없음)
    return _create_token(
        sub=str(uid), typ="access",
        exp=timedelta(minutes=settings.access_token_expires_minutes),
    )

def logout(db: Session, refresh_token: str) -> None:
    # refresh를 즉시 무효화(폐기)
    try:
        payload = _decode_token(refresh_token)
        jti = payload.get("jti")
        auth_repo.mark_refresh_revoked(db, jti)
    except JWTError:
        # 이미 만료/손상되어도 쿠키만 지우면 됨
        pass
