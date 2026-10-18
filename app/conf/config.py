from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

env_path = Path(__file__).resolve().parents[2] / ".env"

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=env_path, env_file_encoding="utf-8", extra="ignore")

    llm_model: str
    llm_base_url: str
    llm_api_key: str

    commerce_api_base_url: str

    database_url: str

    app_host: str
    app_port: int

settings = Settings() # type: ignore

if __name__ == "__main__":
    print(settings.llm_model)

