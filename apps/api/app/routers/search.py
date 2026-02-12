"""Search router for RAG search endpoints."""

from uuid import UUID

from fastapi import APIRouter, HTTPException, status, Query, Depends

from app.dependencies import DbSession, get_current_user
from app.models import User
from app.schemas import (
    RAGSearchRequest,
    SearchResult,
    EventResponse,
    RecentSearchResponse,
    RecentSearchListResponse,
    SaveRecentSearchRequest,
    MessageResponse,
)
from app.services import SearchService, RecentSearchService

router = APIRouter(prefix="/search", tags=["Search"])


@router.post("", response_model=SearchResult)
async def rag_search(
    request: RAGSearchRequest,
    db: DbSession,
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
) -> SearchResult:
    """
    Perform RAG search for artist events.

    This endpoint:
    1. Checks cache for existing results (24-hour TTL)
    2. If cache miss, runs RAG pipeline:
       - Web search via Tavily
       - LLM extraction via GPT-4
       - Embedding generation via OpenAI
       - Vector storage in pgvector
    3. Returns paginated results

    Use force_refresh=true to bypass cache.
    """
    search_service = SearchService(db)

    events, search_id, total, search_time, cached = await search_service.rag_search(
        query=request.query,
        force_refresh=request.force_refresh,
        page=page,
        per_page=per_page,
    )

    return SearchResult(
        searchId=search_id,
        query=request.query,
        events=[EventResponse.from_db_model(e) for e in events],
        total=total,
        searchTime=round(search_time, 2),
        cached=cached,
        page=page,
        hasMore=(page * per_page) < total,
    )


@router.get("/autocomplete")
async def autocomplete_artists(
    db: DbSession,
    q: str = Query(..., min_length=1, max_length=100, description="Search query"),
    limit: int = Query(10, ge=1, le=20, description="Max results"),
):
    """
    Autocomplete artist names.

    This searches existing artists in the database by name.
    For full RAG search, use POST /search.
    """
    from app.services import ArtistService
    from app.schemas import ArtistResponse

    artist_service = ArtistService(db)
    artists, _ = await artist_service.search_artists(q, page=1, per_page=limit)

    return {
        "data": [ArtistResponse.model_validate(a) for a in artists],
    }


# ============== Recent Searches ==============


@router.get("/recent", response_model=RecentSearchListResponse)
async def get_recent_searches(
    db: DbSession,
    current_user: User = Depends(get_current_user),
    limit: int = Query(10, ge=1, le=20, description="Max results"),
) -> RecentSearchListResponse:
    """Get current user's recent search history."""
    recent_search_service = RecentSearchService(db)

    searches = await recent_search_service.get_recent_searches(
        user_id=current_user.id,
        limit=limit,
    )

    return RecentSearchListResponse(
        data=[RecentSearchResponse.from_db_model(s) for s in searches],
    )


@router.post("/recent", response_model=RecentSearchResponse, status_code=status.HTTP_201_CREATED)
async def save_recent_search(
    request: SaveRecentSearchRequest,
    db: DbSession,
    current_user: User = Depends(get_current_user),
) -> RecentSearchResponse:
    """Save a search query to user's history."""
    recent_search_service = RecentSearchService(db)

    search = await recent_search_service.save_recent_search(
        user_id=current_user.id,
        query=request.query,
    )

    return RecentSearchResponse.from_db_model(search)


@router.delete("/recent/{search_id}", response_model=MessageResponse)
async def delete_recent_search(
    search_id: UUID,
    db: DbSession,
    current_user: User = Depends(get_current_user),
) -> MessageResponse:
    """Delete a specific search from history."""
    recent_search_service = RecentSearchService(db)

    deleted = await recent_search_service.delete_recent_search(
        user_id=current_user.id,
        search_id=search_id,
    )

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recent search not found",
        )

    return MessageResponse(message="Recent search deleted")


@router.delete("/recent", response_model=MessageResponse)
async def clear_recent_searches(
    db: DbSession,
    current_user: User = Depends(get_current_user),
) -> MessageResponse:
    """Clear all recent searches for current user."""
    recent_search_service = RecentSearchService(db)

    count = await recent_search_service.clear_recent_searches(current_user.id)

    return MessageResponse(message=f"Cleared {count} recent searches")
