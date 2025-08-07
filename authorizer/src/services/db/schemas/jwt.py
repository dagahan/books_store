from .base_schema import *


class TokenPayload(BaseModel):
    sub: int  # user_id
    sid: str  # session_id
    exp: int  # expiry timestamp


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str


class RegisterResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str


class RefreshAccessResponse(BaseModel):
    access_token: str
    token_type: str

