from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    META_ACCESS_TOKEN: str
    META_PHONE_NUMBER_ID: str
    META_WABA_ID: str
    META_APP_ID: str
    META_APP_SECRET: str
    META_VERIFY_TOKEN: str
    DATABASE_URL: str

    class Config:
        env_file = ".env"

settings = Settings()  # type: ignore[reportCallIssue]