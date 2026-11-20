from contextlib import asynccontextmanager

from fastapi import FastAPI

from dia.api.v1.router import api_router
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

# Register versioned API routes.
app.include_router(
    api_router,
    prefix=settings.api_v1_prefix,
)
