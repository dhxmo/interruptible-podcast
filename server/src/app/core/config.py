import os
from dataclasses import field
from enum import Enum

from pydantic_settings import BaseSettings
from starlette.config import Config


current_file_dir = os.path.dirname(os.path.realpath(__file__))
assets_dir = os.path.join(current_file_dir, "..", "..", "..", "assets")
env_path = os.path.join(current_file_dir, "..", "..", ".env")
config = Config(env_path)


class AppSettings(BaseSettings):
    APP_NAME: str = config("APP_NAME", default="FastAPI app")
    APP_DESCRIPTION: str | None = config("APP_DESCRIPTION", default=None)
    APP_VERSION: str | None = config("APP_VERSION", default=None)
    LICENSE_NAME: str | None = config("LICENSE", default=None)
    CONTACT_NAME: str | None = config("CONTACT_NAME", default=None)
    CONTACT_EMAIL: str | None = config("CONTACT_EMAIL", default=None)


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


class RedisCacheSettings(BaseSettings):
    REDIS_CACHE_HOST: str = config("REDIS_CACHE_HOST", default="localhost")
    REDIS_CACHE_PORT: int = config("REDIS_CACHE_PORT", default=6379)
    REDIS_CACHE_URL: str = f"redis://{REDIS_CACHE_HOST}:{REDIS_CACHE_PORT}"


class RedisQueueSettings(BaseSettings):
    REDIS_QUEUE_HOST: str = config("REDIS_QUEUE_HOST", default="localhost")
    REDIS_QUEUE_PORT: int = config("REDIS_QUEUE_PORT", default=6379)


class RedisRateLimiterSettings(BaseSettings):
    REDIS_RATE_LIMIT_HOST: str = config("REDIS_RATE_LIMIT_HOST", default="localhost")
    REDIS_RATE_LIMIT_PORT: int = config("REDIS_RATE_LIMIT_PORT", default=6379)
    REDIS_RATE_LIMIT_URL: str = (
        f"redis://{REDIS_RATE_LIMIT_HOST}:{REDIS_RATE_LIMIT_PORT}"
    )


class DefaultRateLimitSettings(BaseSettings):
    DEFAULT_RATE_LIMIT_LIMIT: int = config("DEFAULT_RATE_LIMIT_LIMIT", default=10)
    DEFAULT_RATE_LIMIT_PERIOD: int = config("DEFAULT_RATE_LIMIT_PERIOD", default=3600)


class Settings(
    AppSettings,
    ContentGeneratorAPISettings,
    EnvironmentSettings,
    LocalAssetsSetting,
    RedisCacheSettings,
    RedisQueueSettings,
    RedisRateLimiterSettings,
    DefaultRateLimitSettings,
):
    pass


settings = Settings()
