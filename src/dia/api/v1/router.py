
from fastapi import APIRouter

from dia.api.v1.endpoints import documents, health, system

api_router = APIRouter()

api_router.include_router(health.router)
api_router.include_router(system.router)

api_router.include_router(
    documents.router,
    prefix="/documents",
    tags=["Documents"],
)
