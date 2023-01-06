import os

from pydantic import BaseSettings


class _Settings(BaseSettings):
    development_mode: bool = False
    db_url: str
    secret: str
    access_token_expire_days: int = 7
    redis_host: str
    vapid_private_key_path: str
    vapid_public_key_path: str
    push_notification_subject: str


settings = _Settings([f"settings.env", "override.env"])
