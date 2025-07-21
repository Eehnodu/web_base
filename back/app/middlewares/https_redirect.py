from starlette.middleware.httpsredirect import HTTPSRedirectMiddleware
from config.settings import settings

def add_https_redirect(app):
    if settings.env == "prod":
        app.add_middleware(HTTPSRedirectMiddleware)
