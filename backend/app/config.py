from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = "sqlite+aiosqlite:///./dev.db"
    supabase_url: str = "https://muzemjdlrxuewvcdwxpm.supabase.co"
    supabase_api_key: str = ""
    supabase_service_role: str = ""
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    debug: bool = True
    jwt_secret: str = "dev-secret-change-me"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 1440

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


settings = Settings()  # type: ignore[call-arg]
