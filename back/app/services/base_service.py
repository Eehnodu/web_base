"""
attendance_service.py
----------------------

이 모듈은 출결(Attendance) 관련 비즈니스 로직을 처리하는 서비스 계층입니다.

📌 서비스 계층이 필요한 이유:
    - 라우터와 DB repository 사이의 중간 역할을 수행합니다.
    - 단순히 DB에 저장만 하는 것이 아니라, 향후 출결 중복 방지, 알림, 조건 분기 등의 로직을
      이 계층에서 처리할 수 있습니다.
    - 라우터는 "입출력 처리", repository는 "데이터 접근", 서비스는 "업무 로직"을 담당합니다.
"""

from sqlalchemy.orm import Session
from app.repository import base_repo
from app.models import User

def create_user(db: Session, username: str, email: str) -> User:
    return base_repo.create_user(db, username=username, email=email)