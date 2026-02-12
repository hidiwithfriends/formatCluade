from typing import Optional, List
from uuid import UUID
from fastapi import APIRouter, HTTPException, status, Query

from app.dependencies import DbSession
from app.schemas import (
    ArtistResponse,
    ArtistListResponse,
    ArtistCreate,
    EventResponse,
    EventListResponse,
)
from app.services import ArtistService, EventService

router = APIRouter(prefix="/artists", tags=["Artists"])


@router.get("", response_model=ArtistListResponse)
async def list_artists(
    db: DbSession,
    query: Optional[str] = Query(None, description="Search query"),
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
) -> ArtistListResponse:
    """
    List artists with optional search.

    If query is provided, searches by name (English or Korean).
    Otherwise, returns popular artists ordered by follower count.
    """
    artist_service = ArtistService(db)

    if query:
        artists, total = await artist_service.search_artists(query, page, per_page)
    else:
        artists, total = await artist_service.get_popular_artists(page, per_page)

    return ArtistListResponse(
        data=[ArtistResponse.model_validate(a) for a in artists],
        total=total,
        page=page,
        per_page=per_page,
    )


@router.get("/{artist_id}", response_model=ArtistResponse)
async def get_artist(
    artist_id: UUID,
    db: DbSession,
) -> ArtistResponse:
    """Get artist by ID."""
    artist_service = ArtistService(db)
    artist = await artist_service.get_artist_by_id(artist_id)

    if not artist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Artist not found",
        )

    return ArtistResponse.model_validate(artist)


@router.post("", response_model=ArtistResponse, status_code=status.HTTP_201_CREATED)
async def create_artist(
    data: ArtistCreate,
    db: DbSession,
) -> ArtistResponse:
    """
    Create a new artist.

    Note: In production, this should be restricted to admin users.
    """
    artist_service = ArtistService(db)

    # Check if artist already exists
    existing = await artist_service.get_artist_by_name(data.name)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Artist with this name already exists",
        )

    artist = await artist_service.create_artist(data)
    return ArtistResponse.model_validate(artist)


@router.get("/{artist_id}/events", response_model=EventListResponse)
async def get_artist_events(
    artist_id: UUID,
    db: DbSession,
    include_past: bool = Query(False, description="Include past events"),
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
) -> EventListResponse:
    """Get events for a specific artist."""
    artist_service = ArtistService(db)
    event_service = EventService(db)

    # Check artist exists
    artist = await artist_service.get_artist_by_id(artist_id)
    if not artist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Artist not found",
        )

    events, total = await event_service.get_events_by_artist(
        artist_id=artist_id,
        include_past=include_past,
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


@router.get("/{artist_id}/related", response_model=ArtistListResponse)
async def get_related_artists(
    artist_id: UUID,
    db: DbSession,
    limit: int = Query(6, ge=1, le=20, description="Max results"),
) -> ArtistListResponse:
    """
    Get artists related to the given artist.

    Related artists are determined by:
    - Same genre
    - Similar popularity (follower count)
    """
    artist_service = ArtistService(db)

    # Check artist exists
    artist = await artist_service.get_artist_by_id(artist_id)
    if not artist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Artist not found",
        )

    # Get artists with same genre, excluding current artist
    related_artists = await artist_service.get_related_artists(
        artist_id=artist_id,
        genre=artist.genre,
        limit=limit,
    )

    return ArtistListResponse(
        data=[ArtistResponse.model_validate(a) for a in related_artists],
        total=len(related_artists),
        page=1,
        per_page=limit,
    )
