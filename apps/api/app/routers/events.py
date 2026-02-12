"""Events router for event-related endpoints."""

from typing import Optional
from uuid import UUID
from datetime import date

from fastapi import APIRouter, HTTPException, status, Query

from app.dependencies import DbSession
from app.models.event import EventCategory
from app.schemas import EventResponse, EventListResponse
from app.services import EventService

router = APIRouter(prefix="/events", tags=["Events"])


@router.get("", response_model=EventListResponse)
async def list_events(
    db: DbSession,
    query: Optional[str] = Query(None, description="Search query"),
    category: Optional[EventCategory] = Query(None, description="Filter by category"),
    city: Optional[str] = Query(None, description="Filter by city"),
    country: Optional[str] = Query(None, description="Filter by country"),
    from_date: Optional[date] = Query(None, description="Filter from date"),
    to_date: Optional[date] = Query(None, description="Filter to date"),
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
) -> EventListResponse:
    """
    List events with optional filters.

    By default, only returns upcoming events (event_date >= today).
    Use from_date to include past events.
    """
    event_service = EventService(db)

    events, total = await event_service.search_events(
        query=query or "",
        category=category,
        city=city,
        country=country,
        from_date=from_date,
        to_date=to_date,
        page=page,
        per_page=per_page,
    )

    return EventListResponse(
        data=[EventResponse.from_db_model(e) for e in events],
        total=total,
        page=page,
        per_page=per_page,
        has_more=(page * per_page) < total,
    )


@router.get("/{event_id}", response_model=EventResponse)
async def get_event(
    event_id: UUID,
    db: DbSession,
) -> EventResponse:
    """Get event details by ID."""
    event_service = EventService(db)
    event = await event_service.get_event_by_id(event_id)

    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found",
        )

    return EventResponse.from_db_model(event)
