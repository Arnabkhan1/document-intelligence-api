from contextlib import asynccontextmanager

from fastapi import FastAPI

from dia.core.config import get_settings
from dia.core.exception_handlers import register_exception_handlers
from dia.core.logger import get_logger, setup_logging

settings = get_settings()

setup_logging()

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Application starting")

    yield

    logger.info("Application shutting down")


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=(
        "An intelligent document processing, retrieval and question-answering platform."
    ),
    debug=settings.debug,
    lifespan=lifespan,
)

register_exception_handlers(app)


@app.get("/health", tags=["Health"])
async def health_check():
    logger.info("Health check requested")

    return {
        "status": "healthy",
        "service": settings.app_name,
        "version": settings.app_version,
        "environment": settings.app_env,
    }
