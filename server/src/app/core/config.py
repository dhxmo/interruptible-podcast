import os
from dataclasses import field
from enum import Enum

from pydantic_settings import BaseSettings
from starlette.config import Config


current_file_dir = os.path.dirname(os.path.realpath(__file__))
assets_dir = os.path.join(current_file_dir, "..", "..", "..", "assets")
env_path = os.path.join(current_file_dir, "..", "..", ".env")
config = Config(env_path)


class ContentGeneratorAPISettings(BaseSettings):
    OLLAMA_MODEL: str = config("OLLAMA_MODEL", default="qwen2.5:0.5b")
    OLLAMA_LLM_ENDPOINT: str = config(
        "OLLAMA_LLM_ENDPOINT", default="http://127.0.0.1:11434/api/generate"
    )
    OLLAMA_LLM_URL: str = config("OLLAMA_LLM_URL", default="http://127.0.0.1:11434")
    HF_EMBEDDINGS_MODEL_NAME: str = config(
        "HF_EMBEDDINGS_MODEL_NAME", default="all-MiniLM-L6-v2"
    )


class EnvironmentOption(Enum):
    LOCAL = "local"
    STAGING = "staging"
    PRODUCTION = "production"


class LocalAssetsSetting(BaseSettings):
    PROGRESS_JSON: str = config("PROGRESS_JSON", default=f"{assets_dir}/progress.json")


class EnvironmentSettings(BaseSettings):
    ENVIRONMENT: EnvironmentOption = config("ENVIRONMENT", default="local")
    CONFIG_YAML: str = config("CONFIG_YAML", default=f"{current_file_dir}/config.yaml")


class Settings(ContentGeneratorAPISettings, EnvironmentSettings, LocalAssetsSetting):
    pass


settings = Settings()
