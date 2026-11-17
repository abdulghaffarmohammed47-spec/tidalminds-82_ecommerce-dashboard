from pydantic_settings import BaseSettings
from pydantic import field_validator

class Settings(BaseSettings):
    PROJECT_NAME: str = "Smart E-Commerce API"
    DATABASE_URL: str = "postgresql+asyncpg://admin:admin123@localhost:5433/ecommerce_db"
    MONGO_URL: str = "mongodb://admin:admin123@localhost:27018/?authSource=admin"
    MONGO_DB: str = "ecommerce_mongo"
    REDIS_URL: str = "redis://localhost:6379/0"
    JWT_SECRET: str = "supersecretkey"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7 # 1 week
    CORS_ORIGINS: str = "http://localhost:5173,http://127.0.0.1:5173"

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def use_async_postgres_driver(cls, value: str) -> str:
        if value.startswith("postgres://"):
            return value.replace("postgres://", "postgresql+asyncpg://", 1)
        if value.startswith("postgresql://"):
            return value.replace("postgresql://", "postgresql+asyncpg://", 1)
        return value

    class Config:
        env_file = ".env"

settings = Settings()
