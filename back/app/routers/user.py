"""
nfc.py
-------

이 모듈은 NFC 기반 출결 시스템의 API 엔드포인트를 정의합니다.

📌 핵심 역할:
    - 클라이언트(예: 라즈베리파이, 모바일 앱 등)에서 NFC 태그 정보와 함께 POST 요청을 보내면,
      사용자의 출결 기록을 생성하는 엔드포인트를 처리합니다.
    - 실제 출결 기록 생성 로직은 service 계층(attendance_service)에 위임합니다.

✅ 구조 요약:
    - 요청 데이터는 AttendanceCreate 스키마를 통해 검증
    - DB 세션은 Depends(get_db)로 주입
    - 응답은 AttendanceOut 스키마로 직렬화
    - 업무 로직은 service 계층에 분리
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.schemas.user_schema import UserCreate, UserOut
from app.services import user_service
from app.database import get_db

router = APIRouter()

@router.post("/register", response_model=UserOut)
def create_user(
    data: UserCreate,
    db: Session = Depends(get_db)
):
    return user_service.create_user(db, user_id=data.user_id, user_name=data.user_name, user_email=data.user_email, user_password=data.user_password)