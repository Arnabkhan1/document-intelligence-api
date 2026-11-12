
from fastapi import FastAPI


from fastapi import FastAPI

from dia.core.config import get_settings

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=(
        "An intelligent document processing, "
        "retrieval and question-answering platform."
    ),
    debug=settings.debug,
)


@app.get("/health", tags=["Health"])
async def health_check():
    return {
        "status": "healthy",
        "service": settings.app_name,
        "version": settings.app_version,
        "environment": settings.app_env,
    }
