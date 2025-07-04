"""
env.py (Alembic)
------------------

이 파일은 Alembic이 마이그레이션을 실행할 때 사용하는 설정 파일입니다.

📌 주요 역할:
    - SQLAlchemy 모델(Base.metadata)을 Alembic에 연결
    - 현재 실행 환경(Local/Prod)에 따라 DB URL을 동적으로 주입
    - 마이그레이션을 "온라인 모드(DB 직접 반영)" 또는 "오프라인 모드(SQL 출력)"로 실행 가능

FastAPI + SQLAlchemy + Alembic 구성에서 필수적인 브릿지 파일입니다.
"""

from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context

import os
import sys

# ✅ 프로젝트 루트 경로를 sys.path에 추가 (app 경로 인식용)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# ✅ settings에서 DB 연결 정보 동적 로드
from app.config.settings import settings

# ✅ SQLAlchemy Base 객체 (모든 모델의 메타 정보 포함)
from app.models.models import Base  # 모델 정의 위치에 따라 조정 가능

# ✅ Alembic의 설정 파일 객체 (.ini 기준)
config = context.config

# ✅ 동적으로 sqlalchemy.url을 설정 (alembic.ini의 placeholder를 덮어씀)
config.set_main_option("sqlalchemy.url", settings.get_db_url())

# ✅ 로깅 설정 (alembic.ini에서 로깅 설정이 있을 경우 적용)
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# ✅ Alembic이 참고할 SQLAlchemy 메타데이터 (즉, 모델 정의 정보)
target_metadata = Base.metadata

# ▶ 오프라인 마이그레이션 실행 함수 (SQL 파일만 생성, DB 연결 없음)
def run_migrations_offline() -> None:
    """
    오프라인 모드: 데이터베이스에 연결하지 않고
    SQL 문장을 stdout 또는 파일로 출력함
    (보통 SQL 리뷰, 수동 실행 목적)
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,  # 파라미터 바인딩을 리터럴로 출력
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

# ▶ 온라인 마이그레이션 실행 함수 (DB에 직접 적용)
def run_migrations_online() -> None:
    """
    온라인 모드: SQLAlchemy 엔진을 통해 실제 데이터베이스에
    마이그레이션을 적용함
    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,  # 커넥션 풀 사용 안 함 (1회성)
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True  # 컬럼 타입 변경도 감지
        )

        with context.begin_transaction():
            context.run_migrations()

# ▶ 실행 분기 (Alembic이 자동으로 offline/online 모드 판단)
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
