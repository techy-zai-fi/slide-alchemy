from fastapi import APIRouter
from pydantic import BaseModel

from ..services.research_engine import ResearchEngine, ResearchResult
from ..utils.config import load_settings

router = APIRouter(prefix="/api/research", tags=["research"])


class ResearchRequest(BaseModel):
    query: str


class GapAnalysisRequest(BaseModel):
    resource_texts: list[str]
    qa_context: dict


@router.post("/search", response_model=list[ResearchResult])
async def search(req: ResearchRequest):
    settings = load_settings()
    engine = ResearchEngine(serper_api_key=settings.serper_api_key, reddit_client_id=settings.reddit_client_id,
        reddit_client_secret=settings.reddit_client_secret)
    return await engine.search_all(req.query)


@router.post("/gaps")
async def analyze_gaps(req: GapAnalysisRequest):
    from ..models.resource import ParsedContent
    settings = load_settings()
    engine = ResearchEngine(serper_api_key=settings.serper_api_key)
    resources = [ParsedContent(text=t) for t in req.resource_texts]
    gaps = await engine.analyze_gaps(resources, req.qa_context)
    return {"gaps": gaps}


@router.post("/web", response_model=list[ResearchResult])
async def search_web(req: ResearchRequest):
    settings = load_settings()
    engine = ResearchEngine(serper_api_key=settings.serper_api_key)
    return await engine.search_web(req.query)


@router.post("/academic", response_model=list[ResearchResult])
async def search_academic(req: ResearchRequest):
    engine = ResearchEngine()
    return await engine.search_academic(req.query)
