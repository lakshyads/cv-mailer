"""
Sync API endpoints - Thin controller layer for Google Sheets sync operations.

NO BUSINESS LOGIC HERE - just request/response handling.
All business logic is in SyncService.
"""

import logging
from fastapi import APIRouter, Depends, HTTPException, Query, status as http_status

from cv_mailer.services import SyncService
from cv_mailer.api.dependencies import get_sync_service
from cv_mailer.api.schemas.common import MessageResponse

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/sync/applications", response_model=dict)
async def sync_applications(
    dry_run: bool = Query(
        False,
        description=(
            "If true, only sync applications from Google Sheets without "
            "sending emails. If false, sync and send first contact emails."
        ),
    ),
    sync_service: SyncService = Depends(get_sync_service),
):
    """
    Sync job applications from Google Sheets.
    
    When dry_run=False (Sync Applications & Reach Out):
    1. Reads data from Google Sheets
    2. Creates or updates job applications in the database
    3. Sends first contact emails to recruiters
    
    When dry_run=True (Sync Applications):
    1. Reads data from Google Sheets
    2. Creates or updates job applications in the database
    3. Does NOT send emails (dry run mode)
    
    Args:
        dry_run: If True, only sync applications without sending emails.
                 If False, sync and send first contact emails.
        sync_service: Sync service instance
        
    Returns:
        Dictionary with sync results (sent_count, skipped_count, total_rows, message)
    """
    try:
        logger.info(f"API: Syncing applications (dry_run={dry_run})")
        result = sync_service.sync_applications(dry_run=dry_run)
        return result
    except Exception as e:
        logger.error(f"Error syncing applications: {e}", exc_info=True)
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error syncing applications: {str(e)}",
        )


@router.post("/sync/follow-ups", response_model=dict)
async def send_follow_ups(
    dry_run: bool = Query(False, description="If true, don't actually send emails"),
    sync_service: SyncService = Depends(get_sync_service),
):
    """
    Send follow-up emails for applications that need them.
    
    This endpoint:
    1. Finds applications that need follow-up emails (based on FOLLOW_UP_DAYS config)
    2. Sends follow-up emails to recruiters (unless dry_run=True)
    
    Args:
        dry_run: If True, simulate sending follow-ups without actually sending
        sync_service: Sync service instance
        
    Returns:
        Dictionary with follow-up results (sent_count, skipped_count, total_needing, message)
    """
    try:
        logger.info(f"API: Sending follow-ups (dry_run={dry_run})")
        result = sync_service.send_follow_ups(dry_run=dry_run)
        return result
    except Exception as e:
        logger.error(f"Error sending follow-ups: {e}", exc_info=True)
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error sending follow-ups: {str(e)}",
        )

