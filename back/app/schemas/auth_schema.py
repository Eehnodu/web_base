from pydantic import BaseModel
from typing import TypedDict
from typing import Literal
TokenType = Literal["access", "refresh"]

class LoginIn(BaseModel):
    username: str
    password: str

class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    refresh_token: str | None = None

class BaseClaims(TypedDict, total=False):
    sub: str
    type: TokenType
    iat: int
    exp: int
    jti: str