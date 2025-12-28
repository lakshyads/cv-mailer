"""
Common schemas shared across the API.
"""

from typing import Generic, TypeVar, List, Optional, Any
from pydantic import BaseModel
from datetime import datetime

T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated response."""
    
    total: int
    limit: int
    offset: int
    items: List[T]
    sort_by: Optional[str] = None
    order: Optional[str] = None


class TimelineEvent(BaseModel):
    """Timeline event for application history."""
    
    id: str
    type: str
    title: str
    description: str
    timestamp: datetime
    metadata: dict[str, Any] = {}


class MessageResponse(BaseModel):
    """Simple message response."""
    
    message: str


class HealthCheckResponse(BaseModel):
    """Health check response."""
    
    status: str
    version: str
    checks: Optional[dict[str, bool]] = None

