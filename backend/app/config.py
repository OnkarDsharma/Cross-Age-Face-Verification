from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding='utf-8',
        case_sensitive=False,
        extra='ignore'  # This will ignore extra fields in .env
    )
    
    # MongoDB Configuration
    MONGODB_URL: str
    DATABASE_NAME: str = "face_verification_db"
    
    # JWT Configuration
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # File Upload Configuration
    UPLOAD_DIR: str = "uploads"
    MAX_FILE_SIZE: int = 5 * 1024 * 1024  # 5MB
    
    # DeepFace Model Configuration
    DEEPFACE_MODEL: str = "Facenet512"
    VERIFICATION_THRESHOLD: float = 0.4

settings = Settings()