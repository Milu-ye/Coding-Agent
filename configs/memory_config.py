from pydantic_settings import BaseSettings

class MemoryConfig(BaseSettings):
    MEMORY_CONSOLIDATE_THRESHOLD: int = 10

