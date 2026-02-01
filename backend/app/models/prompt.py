from pydantic import BaseModel
from typing import Optional


class VisualDirective(BaseModel):
    theme_name: str = "professional"
    color_palette: list[str] = []
    typography: str = ""
    layout_style: str = "grid"
    data_viz_style: str = "clean charts"
    image_guidance: str = ""


class PromptVariant(BaseModel):
    variant_number: int
    variant_description: str
    visual_directive: VisualDirective
    full_prompt: str = ""


class Prompt(BaseModel):
    project_id: str
    role_section: str = ""
    context_section: str = ""
    resources_summary: str = ""
    slide_plan_section: str = ""
    quality_rules: str = ""
    user_preferences_section: str = ""
    variants: list[PromptVariant] = []
    raw_text: str = ""
