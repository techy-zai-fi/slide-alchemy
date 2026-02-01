from pydantic import BaseModel
from typing import Optional
from enum import Enum


class ModelProvider(str, Enum):
    OLLAMA = "ollama"
    OPENROUTER = "openrouter"
    GROQ = "groq"
    OPENAI = "openai"
    GEMINI = "gemini"


class ProviderConfig(BaseModel):
    provider: ModelProvider
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    model_name: str = ""
    is_configured: bool = False


class AppSettings(BaseModel):
    active_provider: ModelProvider = ModelProvider.OLLAMA
    providers: dict[str, ProviderConfig] = {}
    notebooklm_cookie: Optional[str] = None
    serper_api_key: Optional[str] = None
    reddit_client_id: Optional[str] = None
    reddit_client_secret: Optional[str] = None
    data_dir: str = "~/.slide-alchemy"
