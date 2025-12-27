"""
API endpoints for statistics.
"""

from fastapi import APIRouter, Depends

from cv_mailer.services import ApplicationTracker
from cv_mailer.api.dependencies import get_tracker

router = APIRouter()


@router.get("/statistics")
async def get_statistics(tracker: ApplicationTracker = Depends(get_tracker)):
    """
    Get application statistics.

    Args:
        tracker: Application tracker dependency

    Returns:
        Application statistics
    """
    stats = tracker.get_statistics()
    return stats


@router.get("/statistics/summary")
async def get_statistics_summary(tracker: ApplicationTracker = Depends(get_tracker)):
    """
    Get summary statistics.

    Args:
        tracker: Application tracker dependency

    Returns:
        Summary statistics
    """
    stats = tracker.get_statistics()

    return {
        "total_applications": stats["total_applications"],
        "total_emails_sent": stats["total_emails_sent"],
        "follow_ups_sent": stats["follow_ups_sent"],
        "by_status": stats["by_status"],
    }
