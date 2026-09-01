from pydantic import computed_field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "AgriSim"
    API_V1_STR: str = "/api/v1"

    # Defaults to "localhost" for local scripts/pytest,
    # but gets overridden to "db" by docker-compose.yml inside containers.
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "agrisim"
    POSTGRES_PORT: int = 5432

    @computed_field  # type: ignore[misc]
    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql+psycopg2://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    @computed_field  # type: ignore[misc]
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        return self.DATABASE_URL

    # Defaults to localhost for local execution, overridden by docker-compose for containers
    REDIS_URL: str = "redis://localhost:6379/0"

    ECCC_BASE_URL: str = "https://api.weather.gc.ca/collections/swob-realtime/items"

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
