import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    PROJECT_NAME: str = "Synora AI"
    
    # Database configuration - defaults to SQLite locally
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./research_assistant.db")
    
    # JWT security configs
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-super-secret-key-change-in-production-12345")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440")) # 24 hours
    
    # AI API Keys
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    
    # Whisper settings
    WHISPER_MODEL: str = os.getenv("WHISPER_MODEL", "tiny")
    
    # Media upload dir
    UPLOAD_DIR: str = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "uploads")

settings = Settings()

# Ensure uploads directory exists
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
