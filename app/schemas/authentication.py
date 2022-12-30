from typing import Any

from pydantic import BaseModel


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class ReadVapidKeyResponse(BaseModel):
    key: str
