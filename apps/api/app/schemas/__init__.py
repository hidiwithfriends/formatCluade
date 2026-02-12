# Pydantic Schemas (DTOs)
from app.schemas.common import (
    MessageResponse,
    ErrorDetail,
    ErrorResponse,
    PaginatedResponse,
    PaginationMeta,
)
from app.schemas.user import (
    UserBase,
    UserCreate,
    UserUpdate,
    UserResponse,
    UserWithArtistsResponse,
    UserNotificationSettings,
    UserNotificationUpdate,
    OAuthRequest,
    TokenResponse,
)
from app.schemas.artist import (
    ArtistBase,
    ArtistCreate,
    ArtistUpdate,
    ArtistResponse,
    ArtistListResponse,
    FollowArtistRequest,
    FollowArtistResponse,
    UnfollowArtistResponse,
    ArtistSearchRequest,
)
from app.schemas.event import (
    PriceTier,
    PriceInfo,
    EventBase,
    EventCreate,
    EventUpdate,
    EventResponse,
    EventListResponse,
)
from app.schemas.search import (
    RAGSearchRequest,
    SearchPageRequest,
    SearchResult,
    SearchCacheInfo,
    RecentSearchResponse,
    RecentSearchListResponse,
    SaveRecentSearchRequest,
    DeleteRecentSearchRequest,
)

__all__ = [
    # Common
    "MessageResponse",
    "ErrorDetail",
    "ErrorResponse",
    "PaginatedResponse",
    "PaginationMeta",
    # User
    "UserBase",
    "UserCreate",
    "UserUpdate",
    "UserResponse",
    "UserWithArtistsResponse",
    "UserNotificationSettings",
    "UserNotificationUpdate",
    "OAuthRequest",
    "TokenResponse",
    # Artist
    "ArtistBase",
    "ArtistCreate",
    "ArtistUpdate",
    "ArtistResponse",
    "ArtistListResponse",
    "FollowArtistRequest",
    "FollowArtistResponse",
    "UnfollowArtistResponse",
    "ArtistSearchRequest",
    # Event
    "PriceTier",
    "PriceInfo",
    "EventBase",
    "EventCreate",
    "EventUpdate",
    "EventResponse",
    "EventListResponse",
    # Search
    "RAGSearchRequest",
    "SearchPageRequest",
    "SearchResult",
    "SearchCacheInfo",
    "RecentSearchResponse",
    "RecentSearchListResponse",
    "SaveRecentSearchRequest",
    "DeleteRecentSearchRequest",
]
