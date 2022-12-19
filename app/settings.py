from pydantic import BaseSettings


class _Settings(BaseSettings):
    development_mode: bool
    db_url: str


settings = _Settings()