import logging

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

logger = logging.getLogger(__name__)

from ..models.slide import Slide, SlidePlan, SlideUpdate
from ..services.model_router import ModelRouter

router = APIRouter(prefix="/api/slides", tags=["slides"])
_slide_plans: dict[str, SlidePlan] = {}
model_router = ModelRouter()


class GeneratePlanRequest(BaseModel):
    project_id: str
    qa_context: dict
    resource_summaries: list[str]


@router.post("/generate-plan", response_model=SlidePlan)
async def generate_slide_plan(req: GeneratePlanRequest):
    system_prompt = """You are a presentation architect. Based on the context and resources provided,
create a detailed slide-by-slide plan. For each slide, provide:
- title: A compelling slide title
- key_points: 2-4 bullet points
- supporting_data: Specific data, stats, or quotes to include
- visual_direction: What visual elements this slide should have
- speaker_notes: What the presenter should say

Return as JSON: {"slides": [{"title": "...", "key_points": [...], "supporting_data": [...], "visual_direction": "...", "speaker_notes": "..."}]}"""

    user_message = f"""Presentation Context:
- Audience: {req.qa_context.get('audience', 'General')}
- Goal: {req.qa_context.get('goal', 'Inform')}
- Tone: {req.qa_context.get('tone', 'Professional')}
- Slide Count: {req.qa_context.get('slide_count', '10-20')}
- Key Message: {req.qa_context.get('key_message', '')}
- Visual Style: {req.qa_context.get('visual_style', 'Clean')}
- Sections: {req.qa_context.get('sections', '')}
- Must Include: {req.qa_context.get('must_include', '')}
- Time Limit: {req.qa_context.get('time_limit', 'No limit')}

Resource Summaries:
{chr(10).join(f'- {s[:500]}' for s in req.resource_summaries)}

Generate the slide plan now."""

    if model_router.config:
        response = await model_router.chat(system=system_prompt, history=[], user_message=user_message)
        try:
            import json
            json_start = response.find("{")
            json_end = response.rfind("}") + 1
            if json_start >= 0 and json_end > json_start:
                data = json.loads(response[json_start:json_end])
                slides = [Slide(order=i, title=s.get("title", f"Slide {i+1}"), key_points=s.get("key_points", []),
                    supporting_data=s.get("supporting_data", []), visual_direction=s.get("visual_direction", ""),
                    speaker_notes=s.get("speaker_notes", "")) for i, s in enumerate(data.get("slides", []))]
                plan = SlidePlan(project_id=req.project_id, slides=slides, total_slides=len(slides))
                _slide_plans[req.project_id] = plan
                return plan
        except Exception as e:
            logger.warning(f"Failed to parse LLM slide plan response: {e}")

    sections = [s.strip() for s in req.qa_context.get("sections", "Introduction,Main Content,Conclusion").split(",")]
    slides = [Slide(order=i, title=s, key_points=["Key point 1", "Key point 2"]) for i, s in enumerate(sections)]
    plan = SlidePlan(project_id=req.project_id, slides=slides, total_slides=len(slides))
    _slide_plans[req.project_id] = plan
    return plan


@router.get("/{project_id}", response_model=SlidePlan)
async def get_slide_plan(project_id: str):
    if project_id not in _slide_plans:
        raise HTTPException(status_code=404, detail="Slide plan not found")
    return _slide_plans[project_id]


@router.put("/{project_id}/slide/{slide_id}")
async def update_slide(project_id: str, slide_id: str, update: SlideUpdate):
    plan = _slide_plans.get(project_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Slide plan not found")
    for slide in plan.slides:
        if slide.id == slide_id:
            if update.title is not None: slide.title = update.title
            if update.key_points is not None: slide.key_points = update.key_points
            if update.supporting_data is not None: slide.supporting_data = update.supporting_data
            if update.visual_direction is not None: slide.visual_direction = update.visual_direction
            if update.speaker_notes is not None: slide.speaker_notes = update.speaker_notes
            if update.order is not None: slide.order = update.order
            return {"updated": True}
    raise HTTPException(status_code=404, detail="Slide not found")


@router.post("/{project_id}/slide")
async def add_slide(project_id: str, slide: Slide):
    plan = _slide_plans.get(project_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Slide plan not found")
    plan.slides.append(slide)
    plan.total_slides = len(plan.slides)
    return {"added": True, "slide_id": slide.id}


@router.delete("/{project_id}/slide/{slide_id}")
async def delete_slide(project_id: str, slide_id: str):
    plan = _slide_plans.get(project_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Slide plan not found")
    plan.slides = [s for s in plan.slides if s.id != slide_id]
    plan.total_slides = len(plan.slides)
    return {"deleted": True}


@router.put("/{project_id}/reorder")
async def reorder_slides(project_id: str, slide_ids: list[str]):
    plan = _slide_plans.get(project_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Slide plan not found")
    id_to_slide = {s.id: s for s in plan.slides}
    reordered = []
    for i, sid in enumerate(slide_ids):
        if sid in id_to_slide:
            slide = id_to_slide[sid]
            slide.order = i
            reordered.append(slide)
    plan.slides = reordered
    return {"reordered": True}
