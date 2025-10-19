from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_ignore_empty=True)

    PROJECT_NAME: str = "Key checker"
    DEBUG: bool = True

    DATABASE_URL: str
    ALEMBIC_DATABASE_URL: str

    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    EMAIL_HOST: str = "smtp.gmail.com"
    EMAIL_PORT: int = 587
    EMAIL_FROM: str
    EMAIL_USE_TLS: bool = True
    EMAIL_USE_SSL: bool = False
    EMAIL_HOST_USER: str
    EMAIL_HOST_PASSWORD: str

    FRONTEND_URL: str = "http://localhost:3000"

    SITE_NAME: str = "key_check"
    GOOGLE_CLIENT_ID: str
    GOOGLE_CLIENT_SECRET: str


settings = Settings()
