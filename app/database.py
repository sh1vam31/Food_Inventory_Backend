from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Log database configuration for debugging
logger.info(f"Environment: {settings.environment}")
logger.info(f"Database URL starts with: {settings.database_url[:20]}...")
logger.info(f"Is PostgreSQL: {settings.is_postgresql}")

# Configure engine based on database type
try:
    if settings.is_postgresql:
        # PostgreSQL configuration
        logger.info("Configuring PostgreSQL engine")
        engine = create_engine(
            settings.database_url,
            pool_pre_ping=True,  # Verify connections before use
            pool_recycle=300,    # Recycle connections every 5 minutes
            echo=False           # Set to True for SQL debugging
        )
    else:
        # SQLite configuration
        logger.info("Configuring SQLite engine")
        engine = create_engine(
            settings.database_url,
            connect_args={"check_same_thread": False},  # SQLite specific
            echo=False
        )
    
    logger.info("Database engine created successfully")
    
except Exception as e:
    logger.error(f"Failed to create database engine: {e}")
    logger.error(f"Database URL: {settings.database_url}")
    raise

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class
Base = declarative_base()


# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()