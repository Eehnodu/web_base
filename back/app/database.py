"""
database.py
------------

이 모듈은 FastAPI 애플리케이션의 데이터베이스 연결을 설정하는 곳입니다.

📌 주요 기능:
    - SQLAlchemy 엔진과 세션 생성기 구성
    - `Base` 정의: 모든 모델이 상속해야 할 기반 클래스
    - `get_db()` 함수: FastAPI에서 의존성 주입을 통해 DB 세션을 안전하게 사용하도록 지원

settings.get_db_url()을 통해 로컬/운영 환경을 자동 판별하며,
로컬에서는 SQL 로그를 출력하고, 운영에서는 생략하도록 설정합니다.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config.settings import settings

# 로컬 또는 운영 환경에 따라 DB 연결 URL 결정
SQLALCHEMY_DATABASE_URL = settings.get_db_url()

# SQLAlchemy 엔진 생성 (DB와 연결)
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_pre_ping=True,  # 연결 유효성 확인
    echo=settings.env == "local",  # 로컬 환경이면 SQL 쿼리 출력
    future=True
)

# 세션 팩토리 생성
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# 모든 모델이 상속할 베이스 클래스
Base = declarative_base()

# FastAPI 의존성 주입용 DB 세션 생성기
def get_db():
    """
    FastAPI 라우터에서 의존성으로 사용하기 위한 DB 세션 함수.
    요청 처리 중에는 DB 세션을 열고, 처리가 끝나면 자동으로 닫습니다.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
