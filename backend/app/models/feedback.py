from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class SlideRating(BaseModel):
    slide_id: str
    thumbs_up: bool
    comment: Optional[str] = None


class Feedback(BaseModel):
    project_id: str
    variant_number: int
    overall_rating: int = Field(ge=1, le=5)
    tags: list[str] = []
    slide_ratings: list[SlideRating] = []
    created_at: datetime = Field(default_factory=datetime.now)


class PreferenceProfile(BaseModel):
    preferred_styles: dict[str, float] = {}
    preferred_tones: dict[str, float] = {}
    favorite_palettes: list[list[str]] = []
    bullet_density: str = "medium"
    chart_preferences: list[str] = []
    avg_slide_count: Optional[float] = None
    total_presentations: int = 0
    last_updated: datetime = Field(default_factory=datetime.now)
