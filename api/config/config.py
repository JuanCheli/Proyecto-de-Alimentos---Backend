from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    # Entorno / app
    ENV: str = Field("development", env="ENV")
    APP_NAME: str = Field("mi-app", env="APP_NAME")
    DEBUG: bool = Field(False, env="DEBUG")

    # Supabase
    SUPABASE_URL: Optional[str] = Field(None, env="SUPABASE_URL")
    SUPABASE_ANON_KEY: Optional[str] = Field(None, env="SUPABASE_ANON_KEY")
    SUPABASE_SERVICE_KEY: Optional[str] = Field(None, env="SUPABASE_SERVICE_KEY")
    SUPABASE_JWT_SECRET: Optional[str] = Field(None, env="SUPABASE_JWT_SECRET")

    # Timeout
    REQUEST_TIMEOUT: int = Field(30, env="REQUEST_TIMEOUT")

    # Configuración de pydantic-settings
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )

# Instancia creada para utilizar en todo el proyecto
settings = Settings()
