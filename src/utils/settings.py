from pydantic_settings import BaseSettings
from typing import Dict
import os


class Settings(BaseSettings):
    API_TITLE: str = "Configuration Management API"
    API_VERSION: str = "1.0.0"

    CONFIG_STORAGE_PATH: str = "./ingsoft/configs"
    BACKUP_STORAGE_PATH: str = "./ingsoft/backups"

    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "dev")

    SERVICE_TOKENS: Dict[str, str] = {
        "web-app": "webapp_abc123",
        "api-service": "api_def456",
        "worker": "worker_ghi789"
    }

    ADMIN_TOKENS: Dict[str, str] = {
        "devops": "admin_xyz999",
        "sre": "admin_abc123"
    }

    class Config:
        case_sensitive = True


settings = Settings()
