"""Search schemas for API request/response."""

from datetime import datetime
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel, Field

from app.schemas.event import EventResponse


# ============== Search Request Schemas ==============


class RAGSearchRequest(BaseModel):
    """Schema for RAG search request."""

    query: str = Field(..., min_length=1, max_length=500)
    force_refresh: bool = Field(
        default=False,
        description="Force bypass cache and perform fresh RAG search",
    )


class SearchPageRequest(BaseModel):
    """Schema for paginated search results request."""

    page: int = Field(default=1, ge=1)
    per_page: int = Field(default=20, ge=1, le=100)


# ============== Search Response Schemas ==============


class SearchResult(BaseModel):
    """Schema for search result (matches frontend SearchResult type)."""

    searchId: str
    query: str
    events: List[EventResponse]
    total: int
    searchTime: float  # in seconds
    cached: bool
    page: int
    hasMore: bool


class SearchCacheInfo(BaseModel):
    """Schema for search cache info."""

    query: str
    total_results: int
    search_time_seconds: float
    created_at: datetime
    expires_at: datetime


# ============== Recent Search Schemas ==============


class RecentSearchResponse(BaseModel):
    """Schema for recent search response (matches frontend RecentSearch type)."""

    id: UUID
    query: str
    searchedAt: str  # ISO 8601 format

    class Config:
        from_attributes = True

    @classmethod
    def from_db_model(cls, recent_search) -> "RecentSearchResponse":
        """Convert DB model to response schema."""
        return cls(
            id=recent_search.id,
            query=recent_search.query,
            searchedAt=recent_search.searched_at.isoformat(),
        )


class RecentSearchListResponse(BaseModel):
    """Schema for recent search list."""

    data: List[RecentSearchResponse]


class SaveRecentSearchRequest(BaseModel):
    """Schema for saving a recent search."""

    query: str = Field(..., min_length=1, max_length=500)


class DeleteRecentSearchRequest(BaseModel):
    """Schema for deleting a recent search."""

    search_id: Optional[UUID] = Field(None, description="Specific search ID to delete")
    clear_all: bool = Field(default=False, description="Clear all recent searches")
