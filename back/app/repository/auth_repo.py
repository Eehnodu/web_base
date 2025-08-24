from sqlalchemy.orm import Session
from datetime import datetime, timezone
from app.models.models import User, RefreshSession

# ----- User -----
def get_by_user_id(db: Session, user_id: str) -> User | None:
    return db.query(User).filter(User.user_id == user_id).first()

def create_user(db: Session, user_id: str, user_name: str, user_email: str, password_hash: str) -> User:
    u = User(user_id=user_id, user_name=user_name, user_email=user_email, user_password=password_hash)
    db.add(u)
    db.commit()
    db.refresh(u)
    return u

# ----- RefreshSession -----
def create_refresh_session(
    db: Session, *, user_id: int, jti: str, token_hash: str, expires_at: datetime,
    user_agent: str | None, ip: str | None
) -> RefreshSession:
    rs = RefreshSession(
        user_id=user_id, jti=jti, token_hash=token_hash,
        expires_at=expires_at, user_agent=user_agent, ip=ip
    )
    db.add(rs)
    db.commit()
    db.refresh(rs)
    return rs

def get_refresh_session_by_jti(db: Session, jti: str) -> RefreshSession | None:
    return db.query(RefreshSession).filter(RefreshSession.jti == jti).first()

def mark_refresh_revoked(db: Session, jti: str) -> None:
    rs = get_refresh_session_by_jti(db, jti)
    if rs and not rs.revoked:
        rs.revoked = True
        db.commit()

def touch_refresh_last_used(db: Session, jti: str) -> None:
    rs = get_refresh_session_by_jti(db, jti)
    if rs:
        rs.last_used_at = datetime.now(timezone.utc)
        db.commit()
