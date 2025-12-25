from pydantic_settings import BaseSettings
from typing import Optional
import os
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    # Database configuration with better error handling
    database_url: str = "sqlite:///./food_inventory.db"  # Default fallback
    
    # Security
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    
    # Environment
    environment: str = "development"
    
    class Config:
        env_file = ".env"
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Get DATABASE_URL from environment with better handling
        env_db_url = os.getenv("DATABASE_URL")
        if env_db_url and env_db_url.strip():
            self.database_url = env_db_url.strip()
            logger.info(f"Using DATABASE_URL from environment: {self.database_url[:30]}...")
        else:
            logger.warning("DATABASE_URL not found in environment, using SQLite default")
        
        # Get ENVIRONMENT from environment
        env_environment = os.getenv("ENVIRONMENT")
        if env_environment and env_environment.strip():
            self.environment = env_environment.strip()
        
        # Validate database URL
        if not self.database_url or self.database_url.strip() == "":
            raise ValueError("DATABASE_URL cannot be empty")
        
        logger.info(f"Final configuration - Environment: {self.environment}, DB Type: {'PostgreSQL' if self.is_postgresql else 'SQLite'}")
    
    @property
    def is_production(self) -> bool:
        return self.environment.lower() == "production"
    
    @property
    def is_postgresql(self) -> bool:
        url = self.database_url.lower()
        return url.startswith("postgresql://") or url.startswith("postgres://")


# Create settings instance
try:
    settings = Settings()
except Exception as e:
    logger.error(f"Failed to create settings: {e}")
    # Fallback to basic configuration
    settings = Settings(database_url="sqlite:///./food_inventory.db", environment="development")