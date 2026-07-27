"""
Application settings loaded from environment variables.

Previously used Meta Cloud API credentials.
Now only requires the WaSenderAPI token and database URL.

Required environment variables:
  WASENDER_API_TOKEN  — API token from your WaSender dashboard
  DATABASE_URL        — PostgreSQL connection string (from Render)

Optional:
  SERVER_BASE_URL     — Publicly accessible URL of this service (for logging)
"""

import os

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # WaSender credentials
    WASENDER_API_TOKEN: str = ""

    # Database
    DATABASE_URL: str

    # Optional: base URL of this service (used in logs / future features)
    SERVER_BASE_URL: str = ""

    class Config:
        env_file = ".env"
        extra = "ignore"  # silently ignore any leftover META_* vars in .env


settings = Settings()  # type: ignore[reportCallIssue]