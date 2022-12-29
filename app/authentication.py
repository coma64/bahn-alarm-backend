from datetime import datetime, timedelta, timezone

import jose
from jose import jwt
from passlib.context import CryptContext
from pydantic import BaseModel, ValidationError

from app import settings

JWT_ALGORITHM = jwt.ALGORITHMS.HS256
CRYPT_CONTEXT = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return CRYPT_CONTEXT.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    return CRYPT_CONTEXT.verify(password, password_hash)


class Jwt(BaseModel):
    exp: datetime
    sub: str


def create_access_token(username: str) -> str:
    return jwt.encode(
        Jwt(
            exp=datetime.now() + timedelta(days=settings.access_token_expire_days),
            sub=username,
        ).dict(),
        settings.secret,
        JWT_ALGORITHM,
    )


def get_username(token: str) -> str | None:
    try:
        parsed_jwt = Jwt.parse_obj(
            jwt.decode(token, settings.secret, algorithms=[JWT_ALGORITHM])
        )
    except ValidationError:
        return
    except jose.JWTError:
        return

    if parsed_jwt.exp < datetime.now(timezone.utc):
        return

    return parsed_jwt.sub
