from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str = "sqlite+aiosqlite:///./app.db"
    upload_dir: str = "uploads"
    cors_origins: list[str] = ["http://localhost:5173", "http://localhost:4173"]

    class Config:
        env_file = ".env"

settings = Settings()
