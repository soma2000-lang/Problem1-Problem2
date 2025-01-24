from fastapi import APIRouter

from app.api.routes import items
from app.core.config import settings

api_router = APIRouter()

api_router.include_router(items.router)


if settings.ENVIRONMENT == "local":
    api_router.include_router(private.router)