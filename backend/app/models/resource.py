from pydantic import BaseModel, Field
from enum import Enum
from typing import Optional
import uuid


class ResourceType(str, Enum):
    PDF = "pdf"
    DOCX = "docx"
    PPTX = "pptx"
    TXT = "txt"
    MARKDOWN = "markdown"
    IMAGE = "image"
    YOUTUBE = "youtube"
    WEB_URL = "web_url"
    GOOGLE_DRIVE = "google_drive"
    RAW_TEXT = "raw_text"
    RESEARCH = "research"


class ParsedContent(BaseModel):
    text: str
    sections: list[dict] = Field(default_factory=list)
    metadata: dict = Field(default_factory=dict)


class ResourceCreate(BaseModel):
    type: ResourceType
    source: str
    label: Optional[str] = None
    priority: str = "primary"


class Resource(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    type: ResourceType
    source: str
    label: Optional[str] = None
    priority: str = "primary"
    parsed: Optional[ParsedContent] = None
    status: str = "pending"
    error: Optional[str] = None
