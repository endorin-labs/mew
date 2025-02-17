from fastapi import APIRouter
from app.core.logging import setup_logging


router = APIRouter()
logger = setup_logging(__name__)


@router.get("/", response_model=dict)
async def health_check():
    logger.info("Health check endpoint called")
    return {"healthy": True}
