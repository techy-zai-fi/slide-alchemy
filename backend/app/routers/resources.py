import os
import uuid
import aiofiles
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import Optional

from ..models.resource import Resource, ResourceCreate, ResourceType, ParsedContent
from ..services.resource_parser import ResourceParser
from ..utils.config import DATA_DIR

router = APIRouter(prefix="/api/resources", tags=["resources"])
parser = ResourceParser()

_resources: dict[str, Resource] = {}


@router.post("/upload", response_model=Resource)
async def upload_file(
    file: UploadFile = File(...),
    priority: str = Form("primary"),
    label: Optional[str] = Form(None),
):
    ext = os.path.splitext(file.filename or "")[1].lower()
    type_map = {
        ".pdf": ResourceType.PDF,
        ".docx": ResourceType.DOCX,
        ".pptx": ResourceType.PPTX,
        ".txt": ResourceType.TXT,
        ".md": ResourceType.MARKDOWN,
        ".png": ResourceType.IMAGE,
        ".jpg": ResourceType.IMAGE,
        ".jpeg": ResourceType.IMAGE,
        ".webp": ResourceType.IMAGE,
    }
    resource_type = type_map.get(ext)
    if not resource_type:
        raise HTTPException(status_code=400, detail=f"Unsupported file type: {ext}")

    upload_dir = DATA_DIR / "uploads"
    upload_dir.mkdir(parents=True, exist_ok=True)
    file_id = str(uuid.uuid4())
    file_path = upload_dir / f"{file_id}{ext}"

    async with aiofiles.open(file_path, "wb") as f:
        content = await file.read()
        await f.write(content)

    resource = Resource(
        type=resource_type,
        source=str(file_path),
        label=label or file.filename,
        priority=priority,
        status="parsing",
    )

    try:
        parsed = await parser.parse(resource_type, str(file_path))
        resource.parsed = parsed
        resource.status = "parsed"
    except Exception as e:
        resource.status = "error"
        resource.error = str(e)

    _resources[resource.id] = resource
    return resource


@router.post("/url", response_model=Resource)
async def add_url(body: ResourceCreate):
    resource = Resource(
        type=body.type,
        source=body.source,
        label=body.label,
        priority=body.priority,
        status="parsing",
    )

    try:
        parsed = await parser.parse(body.type, body.source)
        resource.parsed = parsed
        resource.status = "parsed"
    except Exception as e:
        resource.status = "error"
        resource.error = str(e)

    _resources[resource.id] = resource
    return resource


@router.post("/text", response_model=Resource)
async def add_raw_text(body: ResourceCreate):
    resource = Resource(
        type=ResourceType.RAW_TEXT,
        source=body.source,
        label=body.label or "Raw Text",
        priority=body.priority,
        status="parsed",
        parsed=parser.parse_raw_text(body.source),
    )
    _resources[resource.id] = resource
    return resource


@router.get("/", response_model=list[Resource])
async def list_resources():
    return list(_resources.values())


@router.get("/{resource_id}", response_model=Resource)
async def get_resource(resource_id: str):
    if resource_id not in _resources:
        raise HTTPException(status_code=404, detail="Resource not found")
    return _resources[resource_id]


@router.delete("/{resource_id}")
async def delete_resource(resource_id: str):
    if resource_id not in _resources:
        raise HTTPException(status_code=404, detail="Resource not found")
    del _resources[resource_id]
    return {"deleted": True}
