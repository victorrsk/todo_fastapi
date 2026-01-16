from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file='.env', env_file_encoding='utf-8'
    )

    DATABASE_URL: str = ''
    TOKEN_EXPIRE_TIME: int = 0
    ALGORITHM: str = ''
    SECRET_KEY: str = ''
