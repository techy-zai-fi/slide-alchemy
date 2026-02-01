from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
import uuid


class ProjectCreate(BaseModel):
    name: str
    model_provider: str = "ollama"
    model_name: str = "gemma4"


class Project(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    model_provider: str
    model_name: str
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    status: str = "draft"
    resource_ids: list[str] = []
    slide_plan: Optional[dict] = None
    prompt_text: Optional[str] = None
    variant_count: int = 1
