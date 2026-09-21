from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "GenAI Fraud Detection Platform"
    environment: str = "development"
    debug: bool = Field(default=False, validation_alias="APP_DEBUG")
    api_prefix: str = "/api/v1"
    secret_key: str = Field(default="change-me-in-production", min_length=16)
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    database_url: str = "sqlite:///./data/local/genai_fraud.db"
    database_echo: bool = False
    database_pool_pre_ping: bool = True
    supabase_url: str | None = None
    supabase_anon_key: str | None = None
    supabase_service_role_key: str | None = None
    allowed_file_extensions: tuple[str, ...] = ("csv", "xlsx", "xls")
    max_upload_size_mb: int = 200
    cors_origins: list[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]
    upload_directory: Path = Path("data/uploads")
    processed_directory: Path = Path("data/processed")
    report_directory: Path = Path("data/reports")
    log_directory: Path = Path("data/logs")
    model_directory: Path = Path("models/trained")
    vector_store_provider: str = "tfidf"
    chroma_directory: Path = Path("models/vector_store/chroma")
    default_page_size: int = 25

    model_config = SettingsConfigDict(
                env_file=".env",
                env_file_encoding="utf-8",
                case_sensitive=False,
                extra="ignore",
    )

    def ensure_runtime_directories(self) -> None:
        for directory in (
            self.upload_directory,
            self.processed_directory,
            self.report_directory,
            self.log_directory,
            self.model_directory,
            self.chroma_directory,
        ):
            directory.mkdir(parents=True, exist_ok=True)


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    settings.ensure_runtime_directories()
    return settings
