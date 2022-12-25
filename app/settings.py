from pydantic import BaseSettings


class _Settings(BaseSettings):
    development_mode: bool
    db_url: str
    secret: str
    access_token_expire_days: int
    redis_host: str


settings = _Settings(["default.env", "override.env"])
