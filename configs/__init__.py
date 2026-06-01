from pydantic_settings import BaseSettings, SettingsConfigDict

from configs.model_config import ModelConfig


class AppConfig(ModelConfig):

    HOST:str = "0.0.0.0"
    PORT:int = 8000

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False
    )



app_config = AppConfig()