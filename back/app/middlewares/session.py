from starlette.middleware.sessions import SessionMiddleware
from config.settings import settings

def add_session_middleware(app):
    app.add_middleware(
        SessionMiddleware,
        secret_key=settings.SECRET_KEY,  # 필요 시 settings.SECRET_KEY로 치환
        https_only=(settings.env == "prod"),
        same_site="none" if settings.env == "prod" else "lax",
    )
