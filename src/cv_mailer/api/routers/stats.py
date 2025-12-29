"""
Statistics API endpoints - Thin controller layer.

NO BUSINESS LOGIC HERE - just request/response handling.
All business logic is in StatisticsService.
"""

import logging
from fastapi import APIRouter, Depends, HTTPException

from cv_mailer.services import StatisticsService
from cv_mailer.api.dependencies import get_statistics_service

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/statistics")
async def get_statistics(
    service: StatisticsService = Depends(get_statistics_service),
):
    """
    Get application statistics.

    Returns:
        Application statistics
    """
    try:
        return service.get_statistics()
    except Exception as e:
        logger.error(f"Error getting statistics: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/statistics/summary")
async def get_statistics_summary(
    service: StatisticsService = Depends(get_statistics_service),
):
    """
    Get summary statistics.

    Returns:
        Summary statistics
    """
    try:
        return service.get_summary()
    except Exception as e:
        logger.error(f"Error getting statistics summary: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")
