from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from app import models

OAUTH2_SCHEME = OAuth2PasswordBearer("token")
CREDENTIALS_EXCEPTION = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)


async def get_current_user(token: str = Depends(OAUTH2_SCHEME)) -> models.User:
    if user := await models.User.authenticate(token):
        return user
    raise CREDENTIALS_EXCEPTION
