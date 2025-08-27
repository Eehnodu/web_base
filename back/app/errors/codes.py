# app/errors/codes.py
"""
HTTP 상태 코드 모음
-------------------
자주 사용하는 상태 코드와 의미를 정리한 파일.
FastAPI/Starlette의 status 모듈을 import 해서 사용하세요.
"""

from starlette import status

# 2xx: 성공
HTTP_200_OK = status.HTTP_200_OK               # 요청 성공
HTTP_201_CREATED = status.HTTP_201_CREATED     # 리소스 생성 성공
HTTP_204_NO_CONTENT = status.HTTP_204_NO_CONTENT # 성공했지만 응답 본문 없음

# 4xx: 클라이언트 오류
HTTP_400_BAD_REQUEST = status.HTTP_400_BAD_REQUEST   # 잘못된 요청 (파라미터 오류 등)
HTTP_401_UNAUTHORIZED = status.HTTP_401_UNAUTHORIZED # 인증 실패 (토큰 없음/잘못됨)
HTTP_403_FORBIDDEN = status.HTTP_403_FORBIDDEN       # 권한 없음
HTTP_404_NOT_FOUND = status.HTTP_404_NOT_FOUND       # 리소스 없음
HTTP_409_CONFLICT = status.HTTP_409_CONFLICT         # 리소스 충돌 (중복 가입 등)
HTTP_422_UNPROCESSABLE_ENTITY = status.HTTP_422_UNPROCESSABLE_ENTITY # 유효성 검사 실패
HTTP_429_TOO_MANY_REQUESTS = status.HTTP_429_TOO_MANY_REQUESTS       # 요청 과다 (rate limit)

# 5xx: 서버 오류
HTTP_500_INTERNAL_SERVER_ERROR = status.HTTP_500_INTERNAL_SERVER_ERROR # 서버 내부 오류
HTTP_502_BAD_GATEWAY = status.HTTP_502_BAD_GATEWAY   # 잘못된 게이트웨이
HTTP_503_SERVICE_UNAVAILABLE = status.HTTP_503_SERVICE_UNAVAILABLE # 서비스 불가
