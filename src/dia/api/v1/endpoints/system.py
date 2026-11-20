from typing import Annotated

from fastapi import APIRouter, Depends

from dia.core.config import Settings, get_settings
from dia.schemas.system import SystemInfoResponse

router = APIRouter()

SettingsDependency = Annotated[Settings, Depends(get_settings)]


@router.get(
    "/system/info",
    response_model=SystemInfoResponse,
    tags=["System"],
    summary="Get application information",
)
async def get_system_info(
    settings: SettingsDependency,
) -> SystemInfoResponse:
    """
    Return basic application configuration information.
    """

    return SystemInfoResponse(
        app_name=settings.app_name,
        app_version=settings.app_version,
        environment=settings.app_env,
        api_prefix=settings.api_v1_prefix,
    )
