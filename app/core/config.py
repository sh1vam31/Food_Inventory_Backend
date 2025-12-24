from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    # Database configuration
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./food_inventory.db")
    
    # Security
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Environment
    environment: str = os.getenv("ENVIRONMENT", "development")
    
    class Config:
        env_file = ".env"
    
    @property
    def is_production(self) -> bool:
        return self.environment.lower() == "production"
    
    @property
    def is_postgresql(self) -> bool:
        return self.database_url.startswith("postgresql://") or self.database_url.startswith("postgres://")


settings = Settings()