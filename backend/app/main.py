from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routers import resources, chat, settings, research, slides, notebooklm, feedback
from .utils.config import ensure_data_dir


@asynccontextmanager
async def lifespan(app: FastAPI):
    ensure_data_dir()
    yield


app = FastAPI(
    title="SlideAlchemy",
    version="0.1.0",
    description="AI-powered presentation builder backend",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(resources.router)
app.include_router(chat.router)
app.include_router(settings.router)
app.include_router(research.router)
app.include_router(slides.router)
app.include_router(notebooklm.router)
app.include_router(feedback.router)


@app.get("/health")
async def health():
    return {"status": "ok", "version": "0.1.0"}
