import logging
from typing import Annotated

from fastapi import APIRouter, Depends

from dia.core.config import Settings, get_settings
from dia.schemas.health import HealthResponse

router = APIRouter()

logger = logging.getLogger(__name__)

SettingsDependency = Annotated[Settings, Depends(get_settings)]


@router.get(
    "/health",
    response_model=HealthResponse,
    tags=["Health"],
    summary="Check application health",
)
async def health_check(
    settings: SettingsDependency,
) -> HealthResponse:
    """
    Check whether the application is responding.
    """

    logger.info("Health check requested")

    return HealthResponse(
        status="healthy",
        service=settings.app_name,
        version=settings.app_version,
        environment=settings.app_env,
    )
