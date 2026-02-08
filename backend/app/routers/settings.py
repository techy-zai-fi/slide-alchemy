from fastapi import APIRouter
from ..models.settings import AppSettings, ProviderConfig, ModelProvider
from ..utils.config import load_settings, save_settings

router = APIRouter(prefix="/api/settings", tags=["settings"])


@router.get("/", response_model=AppSettings)
async def get_settings():
    return load_settings()


@router.put("/")
async def update_settings(settings: AppSettings):
    save_settings(settings)
    return {"status": "saved"}


@router.put("/provider/{provider}")
async def update_provider(provider: str, config: ProviderConfig):
    settings = load_settings()
    settings.providers[provider] = config
    save_settings(settings)
    return {"status": "saved", "provider": provider}


@router.put("/active-provider")
async def set_active_provider(provider: str):
    settings = load_settings()
    settings.active_provider = ModelProvider(provider)
    save_settings(settings)
    return {"status": "active_provider_set", "provider": provider}
