from .base_schema import *


class TokenPayload(BaseModel):
    sub: int  # user_id
    sid: str  # session_id
    exp: int  # expiry timestamp


class LoginRequest(BaseModel):
    username: str
    password: str
    