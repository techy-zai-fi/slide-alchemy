from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional

from ..services.model_router import ModelRouter, ModelConfig
from ..services.qa_engine import QAEngine, QAState

router = APIRouter(prefix="/api/chat", tags=["chat"])
model_router = ModelRouter()
qa_engine = QAEngine()
_qa_states: dict[str, QAState] = {}


class ConfigureModelRequest(BaseModel):
    provider: str
    model_name: str
    api_key: Optional[str] = None
    base_url: Optional[str] = None


class ChatRequest(BaseModel):
    project_id: str
    message: str


class QAAnswerRequest(BaseModel):
    project_id: str
    answer: str


@router.post("/configure")
async def configure_model(req: ConfigureModelRequest):
    config = ModelConfig(provider=req.provider, model_name=req.model_name, api_key=req.api_key, base_url=req.base_url)
    model_router.set_config(config)
    return {"status": "configured", "provider": req.provider, "model": req.model_name}


@router.post("/qa/start")
async def start_qa(project_id: str):
    state = QAState()
    _qa_states[project_id] = state
    question = qa_engine.get_current_question(state)
    return {"question": question, "state": state.model_dump()}


@router.post("/qa/answer")
async def answer_qa(req: QAAnswerRequest):
    state = _qa_states.get(req.project_id, QAState())
    state = qa_engine.record_answer(state, req.answer)
    _qa_states[req.project_id] = state
    if state.is_complete:
        context = qa_engine.build_context(state)
        return {"complete": True, "context": context, "state": state.model_dump()}
    question = qa_engine.get_current_question(state)
    return {"complete": False, "question": question, "state": state.model_dump()}


@router.post("/qa/context")
async def get_qa_context(project_id: str):
    state = _qa_states.get(project_id)
    if not state:
        return {"error": "No Q&A session found"}
    return qa_engine.build_context(state)


@router.post("/message")
async def chat_message(req: ChatRequest):
    if not model_router.config:
        return {"error": "Model not configured"}
    response = await model_router.chat(system="You are SlideAlchemy, an AI presentation design assistant.", history=[], user_message=req.message)
    return {"response": response}


@router.post("/message/stream")
async def chat_message_stream(req: ChatRequest):
    if not model_router.config:
        return {"error": "Model not configured"}
    async def generate():
        async for chunk in model_router.chat_stream(system="You are SlideAlchemy, an AI presentation design assistant.", history=[], user_message=req.message):
            yield f"data: {chunk}\n\n"
        yield "data: [DONE]\n\n"
    return StreamingResponse(generate(), media_type="text/event-stream")
