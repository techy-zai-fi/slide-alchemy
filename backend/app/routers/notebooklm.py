import asyncio
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from pathlib import Path

from ..services.notebooklm_bridge import NotebookLMBridge
from ..services.prompt_engine import PromptEngine
from ..utils.config import load_settings, DATA_DIR

router = APIRouter(prefix="/api/notebooklm", tags=["notebooklm"])
prompt_engine = PromptEngine()

_generation_status: dict[str, dict] = {}


class GenerateRequest(BaseModel):
    project_id: str
    title: str
    sources: list[dict]
    prompts: list[dict]  # [{variant_number, full_prompt}]


class PromptBuildRequest(BaseModel):
    project_id: str
    qa_context: dict
    slides: list[dict]
    resource_summaries: list[str]
    variant_count: int = 1


@router.post("/build-prompt")
async def build_prompt(req: PromptBuildRequest):
    from ..models.slide import Slide, SlidePlan
    slides = [Slide(**s) for s in req.slides]
    plan = SlidePlan(project_id=req.project_id, slides=slides, total_slides=len(slides))

    prompt = prompt_engine.build_prompt(
        qa_context=req.qa_context,
        slide_plan=plan,
        resource_summaries=req.resource_summaries,
        variant_count=req.variant_count,
    )
    return prompt.model_dump()


@router.post("/generate")
async def generate_presentations(req: GenerateRequest):
    settings = load_settings()
    if not settings.notebooklm_cookie:
        raise HTTPException(status_code=400, detail="NotebookLM cookie not configured")

    bridge = NotebookLMBridge(cookie=settings.notebooklm_cookie)
    _generation_status[req.project_id] = {
        "status": "generating",
        "total_variants": len(req.prompts),
        "completed": 0,
        "results": [],
    }

    results = []
    for prompt_data in req.prompts:
        try:
            result = await bridge.generate_variant(
                title=req.title,
                sources=req.sources,
                prompt=prompt_data["full_prompt"],
                variant_num=prompt_data["variant_number"],
            )
            results.append(result)
            _generation_status[req.project_id]["completed"] += 1
            _generation_status[req.project_id]["results"].append(result)
        except Exception as e:
            results.append({
                "variant_number": prompt_data["variant_number"],
                "error": str(e),
            })
            _generation_status[req.project_id]["completed"] += 1

    _generation_status[req.project_id]["status"] = "done"
    return {"results": results}


@router.get("/status/{project_id}")
async def get_status(project_id: str):
    return _generation_status.get(project_id, {"status": "not_started"})


@router.get("/download/{filename}")
async def download_file(filename: str):
    file_path = DATA_DIR / "downloads" / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(str(file_path), filename=filename, media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation")
