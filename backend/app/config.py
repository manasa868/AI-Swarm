"""AI Swarm Application Configuration."""
from pydantic_settings import BaseSettings
from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent.parent
WORKSPACE_DIR = BASE_DIR
GENERATED_DIR = BASE_DIR / "generated_projects"
DOCUMENTS_DIR = BASE_DIR / "documents"
UPLOADS_DIR = BASE_DIR / "uploads"
DATA_DIR = BASE_DIR / "sample_data"

# Ensure directories exist
for directory in [GENERATED_DIR, DOCUMENTS_DIR, UPLOADS_DIR, DATA_DIR]:
    directory.mkdir(parents=True, exist_ok=True)


class Settings(BaseSettings):
    PROJECT_NAME: str = "AI Swarm: From Individual to Intelligent Teams"
    VERSION: str = "1.0.0"
    API_V1_PREFIX: str = "/api"
    
    # Storage Paths
    BASE_DIR: Path = BASE_DIR
    GENERATED_DIR: Path = GENERATED_DIR
    DOCUMENTS_DIR: Path = DOCUMENTS_DIR
    UPLOADS_DIR: Path = UPLOADS_DIR
    DATA_DIR: Path = DATA_DIR
    
    # Environment & LLM Configuration
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    DEMO_MODE: bool = os.getenv("DEMO_MODE", "true").lower() in ("true", "1", "yes")
    
    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", f"sqlite:///{BASE_DIR / 'ai_swarm.db'}"
    )
    
    # Max Retries for Coder <-> Tester Correction Loop
    MAX_TEST_RETRIES: int = 3
    
    # File limits
    MAX_FILE_SIZE_MB: int = 25
    ALLOWED_EXTENSIONS: list[str] = [
        "txt", "pdf", "docx", "csv", "json", "py", "java", "js", "ts", "md"
    ]

    class Config:
        env_file = ".env"
        extra = "allow"


settings = Settings()
