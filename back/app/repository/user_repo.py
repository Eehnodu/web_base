"""
attendance_repo.py
-------------------

이 모듈은 출결(근태) 관련 DB 조작 로직을 담당하는 '레포지토리(Repository)' 계층입니다.

📌 Repository란?
    - 데이터베이스에 직접 접근하는 함수를 모아둔 계층입니다.
    - API 라우터나 서비스 계층에서 직접 SQLAlchemy 세션을 다루지 않고,
      이 repository를 통해 간접적으로 데이터베이스를 조작합니다.
    - 유지보수성과 테스트 효율성을 높여줍니다.

이 파일에서는 출결 로그(`AttendanceLog`)를 생성하는 기능을 제공합니다.
"""

from sqlalchemy.orm import Session
from app.models import User

def create_user(db: Session, user_id: str, user_name: str, user_email: str, user_password: str) -> User:
    new_user = User(user_id=user_id, user_name=user_name, user_email=user_email, user_password=user_password) 
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user