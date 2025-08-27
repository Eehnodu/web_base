# app/routers/user.py
"""
user.py
-------

사용자 관련 API (회원가입 등)

✅ 규칙
- 요청 바디: Pydantic 스키마로 검증 (422 자동)
- 성공 응답: JSON:API 문서 (application/vnd.api+json)
- 오류 응답: 전역 핸들러가 RFC 7807로 변환
"""

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.services import user_service
from app.schemas.user_schema import UserCreate           # ✅ 요청 스키마 사용
from app.schemas.jsonapi import single_doc, resource
from app.config.settings import settings

router = APIRouter(tags=["user"])  # ← prefix 없음 (패턴 B: main.py에서 /api/user 부여)

# 회원가입
@router.post("/register", status_code=status.HTTP_201_CREATED)
def create_user(data: UserCreate,                      # ✅ 명시적으로 UserCreate로 검증
                response: Response,
                db: Session = Depends(get_db)):
    user = user_service.create_user(
        db,
        user_id=data.user_id,
        user_name=data.user_name,
        user_email=data.user_email,
        user_password=data.user_password,
    )

    # Location 헤더 + JSON:API
    response.headers["Location"] = f"{settings.API_PREFIX}/user/{user.id}"
    response.media_type = "application/vnd.api+json"
    doc = single_doc(
        resource("user", user.id, {
            "user_id": user.user_id,
            "user_name": user.user_name,
            "user_email": user.user_email,
        }),
        self_url=f"{settings.API_PREFIX}/user/{user.id}",
    )
    return doc.model_dump()
