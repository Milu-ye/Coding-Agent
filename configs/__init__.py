from pydantic_settings import BaseSettings, SettingsConfigDict

from configs.memory_config import MemoryConfig
from configs.model_config import ModelConfig


class AppConfig(ModelConfig,MemoryConfig):

    HOST:str = "0.0.0.0"
    PORT:int = 8000

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False
    )



app_config = AppConfig()