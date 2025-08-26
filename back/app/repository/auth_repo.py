from sqlalchemy.orm import Session
from datetime import datetime, timezone
from app.models.models import User, RefreshSession

# User 관련 Repository 함수
def get_by_user_id(db: Session, user_id: str) -> User | None:
    """
    user_id(로그인용 아이디)로 사용자 조회
    - 없으면 None 반환
    """
    return db.query(User).filter(User.user_id == user_id).first()

# RefreshSession 관련 Repository 함수
def create_refresh_session(
    db: Session, *, user_id: int, jti: str, token_hash: str, expires_at: datetime,
    user_agent: str | None, ip: str | None
) -> RefreshSession:
    """
    새로운 RefreshSession 생성
    - refresh_token 원문은 저장하지 않고 해시(token_hash)만 저장
    - jti(토큰 고유 식별자), 만료 시간, 클라이언트 정보(User-Agent, IP) 함께 저장
    """
    rs = RefreshSession(
        user_id=user_id,
        jti=jti,
        token_hash=token_hash,
        expires_at=expires_at,
        user_agent=user_agent,
        ip=ip
    )
    db.add(rs)
    db.commit()
    db.refresh(rs)
    return rs

def get_refresh_session_by_jti(db: Session, jti: str) -> RefreshSession | None:
    """
    jti(토큰 고유 ID)로 RefreshSession 조회
    - 없으면 None 반환
    """
    return db.query(RefreshSession).filter(RefreshSession.jti == jti).first()

def mark_refresh_revoked(db: Session, jti: str) -> None:
    """
    특정 RefreshSession을 폐기(revoked=True 처리)
    - 로그아웃 시 호출
    - 이미 revoke 되지 않았다면 True로 변경 후 commit
    """
    rs = get_refresh_session_by_jti(db, jti)
    if rs and not rs.revoked:
        rs.revoked = True
        db.commit()

def touch_refresh_last_used(db: Session, jti: str) -> None:
    """
    RefreshSession의 마지막 사용 시각(last_used_at) 업데이트
    - /refresh API 호출 시마다 실행
    """
    rs = get_refresh_session_by_jti(db, jti)
    if rs:
        rs.last_used_at = datetime.now(timezone.utc)
        db.commit()
