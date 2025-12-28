"""
Statistics API endpoints - Thin controller layer.

NO BUSINESS LOGIC HERE - just request/response handling.
All business logic is in StatisticsService.
"""

from fastapi import APIRouter, Depends

from cv_mailer.services import StatisticsService
from cv_mailer.api.dependencies import get_statistics_service

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
    return service.get_statistics()


@router.get("/statistics/summary")
async def get_statistics_summary(
    service: StatisticsService = Depends(get_statistics_service),
):
    """
    Get summary statistics.

    Returns:
        Summary statistics
    """
    return service.get_summary()
