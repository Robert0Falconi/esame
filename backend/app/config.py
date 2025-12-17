from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql://biblioteca:biblioteca123@db:5432/biblioteca"
    
    # API
    API_V1_PREFIX: str = "/api/v1"
    PROJECT_NAME: str = "Sistema Gestione Biblioteca"
    
    # Business Rules
    DEFAULT_LOAN_DAYS: int = 14
    PENALTY_PER_DAY: float = 0.50  # Euro per giorno di ritardo
    MAX_LOANS_PER_USER: int = 3  # Limite prestiti simultanei
    
    # CORS
    BACKEND_CORS_ORIGINS: list = ["http://localhost:5173", "http://localhost:8080", "http://localhost:3000"]
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()