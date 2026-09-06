from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="DATA_SOURCE_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    output_dir: Path = Field(default=Path("./data"))
    headless: bool = Field(default=True)
    timeout_s: int = Field(default=30, ge=1, le=600)
    max_retries: int = Field(default=3, ge=0, le=10)
    log_level: str = Field(default="INFO")
    user_agent: str = Field(
        default="Mozilla/5.0 (compatible; StackinDataSource/0.1; +https://stackin.io)"
    )
    public_base_url: str = Field(
        default="https://raw.githubusercontent.com/stackin-io/data-source/master/data",
        description="Base URL where the scraped data folder is publicly served. Used to "
        "render sitemap-style URLs in manifest.json so downstream consumers can fetch files.",
    )
    browse_base_url: str = Field(
        default="https://github.com/stackin-io/data-source/tree/master/data",
        description="Base URL for folder links. raw.githubusercontent serves files only "
        "and 404s on any directory, so folders are linked through the GitHub tree view.",
    )


def get_settings() -> Settings:
    return Settings()
