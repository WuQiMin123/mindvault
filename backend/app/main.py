import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.core.logging import setup_logging
from app.database import init_db

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    await init_db()

    # 启动自检
    if not settings.llm_api_key:
        logger.warning("LLM_API_KEY 未配置 — AI 摘要和打标签功能将不可用")
    if not settings.database_url:
        logger.warning("DATABASE_URL 未配置，将使用默认 SQLite")
    logger.info("started | host=%s port=%s", settings.host, settings.port)
    yield
    logger.info("mindvault stopped")


app = FastAPI(
    title="MindVault API",
    version="0.2.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health():
    return {"status": "ok"}


from app.api.v1.router import api_router  # noqa: E402

app.include_router(api_router, prefix="/api/v1")
