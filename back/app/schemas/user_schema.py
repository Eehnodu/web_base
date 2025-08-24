"""
attendance.py
---------------

이 모듈은 출결(Attendance) API에서 사용하는 데이터 스키마(Pydantic 모델)를 정의합니다.

📌 주요 목적:
    - API 요청 시 들어오는 데이터를 검증 및 구조화 (입력 스키마)
    - API 응답 데이터를 직렬화하여 클라이언트에 반환 (출력 스키마)
    - SQLAlchemy 모델과 연동되어 데이터베이스 객체를 안전하게 변환 가능

⚙️ FastAPI에서는 모든 요청/응답 데이터를 Pydantic 모델로 관리함으로써:
    - 타입 검증이 자동으로 이루어지고
    - Swagger 문서도 자동 생성되며
    - 데이터 흐름이 명확해집니다
"""

from pydantic import BaseModel
from datetime import datetime

class UserCreate(BaseModel):
    user_id: str    
    user_name: str
    user_email: str
    user_password: str

class UserOut(BaseModel):
    id: int
    user_id: str
    user_name: str
    user_email: str
    user_password: str
    user_created_at: datetime
    user_updated_at: datetime

    class Config:
        from_attributes = True