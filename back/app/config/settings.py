"""
settings.py
------------

이 모듈은 FastAPI 애플리케이션에서 사용할 환경 설정을 중앙에서 관리하는 설정 파일입니다.

- `pydantic_settings.BaseSettings`를 기반으로 하여 .env 파일에서 환경 변수들을 자동으로 불러옵니다.
- 로컬과 운영 환경에서 서로 다른 DB 연결 정보를 자동으로 구분하여 적용합니다.
- 전체 프로젝트에서 `settings` 객체 하나로 모든 설정 정보를 일관되게 접근할 수 있도록 구성됩니다.

✅ 주요 목적:
    - 설정을 코드와 분리 (.env에 민감 정보 저장)
    - 실행 환경(로컬/운영)에 따라 동적으로 설정 전환
    - DB 연결, API 기본 정보 등 프로젝트 전체 설정을 중앙 집중화
"""

from pydantic_settings import BaseSettings
import os
import socket

# 환경설정 클래스 (BaseSettings 상속 → .env에서 값 자동 로드)
class Settings(BaseSettings):
    # 프로젝트 관련 메타 정보
    PROJECT_NAME: str = "Base App"  # 프로젝트 이름
    API_PREFIX: str = "/api"           # API 엔드포인트 prefix

    # 공통 설정
    mysql_port: int = 3306             # MySQL 포트 (로컬/운영 동일하게 사용)

    # 로컬 개발 환경용 DB 설정
    local_mysql_user: str              # 로컬 DB 사용자 이름
    local_mysql_password: str          # 로컬 DB 비밀번호
    local_mysql_host: str              # 로컬 DB 호스트 (예: localhost)
    local_mysql_db: str                # 로컬 DB 이름

    # 운영 환경용 DB 설정
    prod_mysql_user: str               # 운영 DB 사용자 이름
    prod_mysql_password: str           # 운영 DB 비밀번호
    prod_mysql_host: str               # 운영 DB 호스트 (예: RDS, 외부 서버 등)
    prod_mysql_db: str                 # 운영 DB 이름

    # 환경 변수 파일 경로 설정 (.env 파일에서 값을 불러옴)
    class Config:
        env_file = ".env"

    @property
    def env(self) -> str:
        """
        현재 실행 환경을 자동으로 판별하는 속성.

        - 로컬 PC나 라즈베리파이 환경이면 "local"
        - 그 외 서버/운영 환경이면 "prod"로 간주
        """
        hostname = socket.gethostname()
        return "local" if "DESKTOP" in hostname or "raspberry" in hostname else "prod"

    def get_db_url(self) -> str:
        """
        현재 환경(local 또는 prod)에 따라 SQLAlchemy DB 연결 URL을 반환하는 함수.
        """
        if self.env == "prod":
            # 운영용 DB URL 구성
            return (
                f"mysql+pymysql://{self.prod_mysql_user}:{self.prod_mysql_password}"
                f"@{self.prod_mysql_host}:{self.mysql_port}/{self.prod_mysql_db}"
            )
        # 로컬용 DB URL 구성
        return (
            f"mysql+pymysql://{self.local_mysql_user}:{self.local_mysql_password}"
            f"@{self.local_mysql_host}:{self.mysql_port}/{self.local_mysql_db}"
        )

# 전역에서 import하여 설정을 사용할 수 있도록 객체 생성
settings = Settings()
