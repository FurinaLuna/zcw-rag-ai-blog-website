from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from loguru import logger

from app.core.config import settings
from app.core.logging import setup_logging
from app.core.redis import close_redis
from app.middleware.cors import setup_cors
from app.middleware.exception import exception_handler_middleware
from app.middleware.rate_limit import rate_limit_middleware
from app.routers import admin, monitor, public, rag


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    setup_logging()
    logger.info(f"Starting {settings.log_level} server...")
    yield
    await close_redis()
    logger.info("Server shut down")


app = FastAPI(
    title="智能内容平台 API",
    description="基于混合渲染与PgVector向量检索的智能内容服务平台",
    version="1.0.0",
    lifespan=lifespan,
)

setup_cors(app)

app.middleware("http")(rate_limit_middleware)
app.middleware("http")(exception_handler_middleware)


@app.middleware("http")
async def request_logging_middleware(request: Request, call_next):
    from time import time

    start = time()
    response = await call_next(request)
    duration = time() - start
    logger.info(f"{request.method} {request.url.path} [{response.status_code}] {duration:.3f}s")
    return response


@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    return JSONResponse(
        status_code=404,
        content={"success": False, "data": None, "message": "Not found"},
    )


@app.exception_handler(422)
async def validation_handler(request: Request, exc):
    return JSONResponse(
        status_code=422,
        content={
            "success": False,
            "data": {"detail": exc.errors() if hasattr(exc, "errors") else str(exc)},
            "message": "Validation error",
        },
    )


app.include_router(public.router, prefix="/api/v1/public", tags=["前台开放"])
app.include_router(admin.router, prefix="/api/v1/admin", tags=["后台管理"])
app.include_router(rag.router, prefix="/api/v1/rag", tags=["RAG问答"])
app.include_router(monitor.router, prefix="/api/v1/monitor", tags=["监控"])


@app.get("/api/v1/health")
async def health_check():
    return {"status": "ok", "version": "1.0.0"}
