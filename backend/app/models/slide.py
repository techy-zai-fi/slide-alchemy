from pydantic import BaseModel, Field
from typing import Optional
import uuid


class Slide(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    order: int
    title: str
    key_points: list[str] = []
    supporting_data: list[str] = []
    source_refs: list[str] = []
    visual_direction: str = ""
    speaker_notes: str = ""


class SlideUpdate(BaseModel):
    title: Optional[str] = None
    key_points: Optional[list[str]] = None
    supporting_data: Optional[list[str]] = None
    visual_direction: Optional[str] = None
    speaker_notes: Optional[str] = None
    order: Optional[int] = None


class SlidePlan(BaseModel):
    project_id: str
    slides: list[Slide] = []
    total_slides: int = 0
    estimated_duration_min: Optional[int] = None
