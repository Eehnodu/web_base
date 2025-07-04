"""
FastAPI 앱 진입점 (main.py)
----------------------------

이 모듈은 FastAPI 애플리케이션을 생성하고 설정하는 진입점입니다.

📌 주요 역할:
    - 앱 인스턴스 생성
    - CORS 미들웨어 등록
    - 로컬 환경에서 DB 테이블 자동 생성
    - 샘플 API 라우터 등록 (예: User 생성 등)

이 구조를 사용하면 `create_app()`을 통해 테스트, 배포, 커스터마이징이 쉬워집니다.
"""

from fastapi import FastAPI
from back.app.routers import base
from app.config.settings import settings
from app.middlewares.cors import add_cors
from app.database import engine, Base
import app.models  # 모델 자동 인식용 import

def create_app() -> FastAPI:
    """
    FastAPI 앱 인스턴스를 생성하고 설정 구성(CORS, DB, 라우터 등)을 등록하는 함수입니다.
    """
    app = FastAPI(title=settings.PROJECT_NAME)

    # CORS 미들웨어 등록
    add_cors(app)
    
    # 로컬 환경에서만 DB 테이블 자동 생성
    if settings.env == "local":
        Base.metadata.create_all(bind=engine)

    # 샘플 라우터 등록
    app.include_router(base.router, prefix=settings.API_PREFIX)

    return app

# 앱 인스턴스 실행을 위한 전역 객체
app = create_app()
