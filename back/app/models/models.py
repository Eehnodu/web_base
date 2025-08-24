"""
models.py
----------

이 파일은 SQLAlchemy의 ORM(Object-Relational Mapping)을 활용해
데이터베이스 테이블 구조를 정의하는 파일입니다.

모든 테이블 모델 클래스는 공통적으로 Base 클래스를 상속받습니다.
Base는 app/database.py 에서 선언되며, 이는 SQLAlchemy의 declarative_base()를 기반으로 합니다.

Base를 상속받는 모든 클래스는 실제 DB 테이블로 매핑되며,
Alembic 등의 마이그레이션 도구에서도 자동으로 인식됩니다.

"""

from app.database import Base
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.sql import func

class User(Base):
    __tablename__ = "tb_user"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(100), unique=True, nullable=False)
    user_name = Column(String(100), nullable=False)
    user_email = Column(String(100), unique=True, nullable=False)
    user_password = Column(String(255), nullable=False)
    user_created_at = Column(DateTime(timezone=True), server_default=func.now())
    user_updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class RefreshSession(Base):
    __tablename__ = "tb_token"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("tb_user.id"), nullable=False)
    # JWT 'jti'(고유 ID) + 토큰 본문 해시(평문 저장 금지)
    jti = Column(String(36), nullable=False, index=True)
    token_hash = Column(String(64), nullable=False, index=True)  # sha256 hex
    # 만료/폐기 및 감사 용도
    expires_at = Column(DateTime(timezone=True), nullable=False)
    revoked = Column(Boolean, default=False, nullable=False)
    user_agent = Column(String(255), nullable=True)
    ip = Column(String(64), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_used_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
