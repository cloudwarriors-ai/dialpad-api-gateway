from pydantic_settings import BaseSettings
import os


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables
    """
    # API settings
    API_TITLE: str = "Dialpad Platform Microservice"
    API_DESCRIPTION: str = "Microservice for Dialpad platform integrations with SSOT field mapping"
    API_VERSION: str = "1.0.0"
    DOCS_URL: str = "/docs"
    REDOC_URL: str = "/redoc"
    
    # Database settings
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://dialpad_user:dialpad_password@microservice_db:5432/dialpad_microservice")
    DATABASE_HOST: str = os.getenv("DATABASE_HOST", "microservice_db")
    DATABASE_PORT: int = int(os.getenv("DATABASE_PORT", 5432))
    DATABASE_NAME: str = os.getenv("DATABASE_NAME", "dialpad_microservice")
    DATABASE_USER: str = os.getenv("DATABASE_USER", "dialpad_user")
    DATABASE_PASSWORD: str = os.getenv("DATABASE_PASSWORD", "dialpad_password")
    
    # Application settings
    ENV: str = os.getenv("ENV", "development")
    DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    # Integration settings
    MAIN_ETL_URL: str = os.getenv("MAIN_ETL_URL", "http://backend:8030")
    MAIN_ETL_API_KEY: str = os.getenv("MAIN_ETL_API_KEY", "")
    
    # Dialpad API settings
    DIALPAD_API_KEY: str = os.getenv("DIALPAD_API_KEY", "")
    DIALPAD_API_SECRET: str = os.getenv("DIALPAD_API_SECRET", "")
    
    # CORS settings
    CORS_ORIGINS: list = ["*"]  # Update with actual origins in production
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: list = ["*"]
    CORS_ALLOW_HEADERS: list = ["*"]


settings = Settings()