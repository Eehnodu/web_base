"""
cors.py
--------

이 모듈은 FastAPI 애플리케이션에서 CORS(Cross-Origin Resource Sharing) 설정을 적용하기 위한 미들웨어 구성 파일입니다.

CORS는 프론트엔드(React, Vue 등)와 백엔드(FastAPI)가 서로 다른 도메인에서 통신할 때,
브라우저가 요청을 차단하지 않도록 허용해주는 보안 메커니즘입니다.

이 파일에서는 `add_cors` 함수를 통해 FastAPI 앱 인스턴스에 CORS 미들웨어를 등록하고,
필요한 도메인, 메서드, 헤더에 대해 접근을 허용하는 정책을 정의합니다.

※ 주의:
- 개발 환경에서는 모든 도메인("*")을 허용해도 되지만,
- 운영 환경에서는 `allow_origins`에 신뢰 가능한 도메인만 명시하는 것이 매우 중요합니다.
"""

from fastapi.middleware.cors import CORSMiddleware

from back.app.config import settings

def add_cors(app):
    """
    FastAPI 애플리케이션에 CORS 미들웨어를 추가하는 함수.

    Args:
        app (FastAPI): FastAPI 인스턴스

    설명:
        - allow_origins=["*"]:
            모든 도메인에서의 요청을 허용. 개발 중에는 편리하지만, 배포 시에는 보안상 위험.
            운영 환경에서는 ["https://yourdomain.com"] 등으로 제한 필요.

        - allow_credentials=True:
            인증 쿠키나 Authorization 헤더 등의 자격 증명을 허용.

        - allow_methods=["*"]:
            모든 HTTP 메서드(GET, POST, PUT, DELETE 등)를 허용.

        - allow_headers=["*"]:
            모든 HTTP 요청 헤더를 허용. 예: Content-Type, Authorization 등.
    """
    if settings.env == "prod":
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["미정"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
    else:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],    # 모든 출처 허용 (운영 시 도메인 제한 권장)
            allow_credentials=True, # 쿠키/인증 헤더 포함 허용
            allow_methods=["*"],    # 모든 HTTP 메서드 허용
            allow_headers=["*"],    # 모든 헤더 허용
        )