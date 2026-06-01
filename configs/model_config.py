from pydantic_settings import BaseSettings


class ModelConfig(BaseSettings):
    BASE_URL: str = ""
    MODEL: str = ""
    API_KEY: str = ""