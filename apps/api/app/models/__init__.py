# SQLAlchemy Models
from app.models.base import UUIDMixin, TimestampMixin
from app.models.user import User, AuthProvider
from app.models.artist import Artist, UserArtist
from app.models.event import Event, EventCategory
from app.models.embedding import EventEmbedding, EMBEDDING_DIMENSION
from app.models.search import SearchCache, RecentSearch

__all__ = [
    "UUIDMixin",
    "TimestampMixin",
    "User",
    "AuthProvider",
    "Artist",
    "UserArtist",
    "Event",
    "EventCategory",
    "EventEmbedding",
    "EMBEDDING_DIMENSION",
    "SearchCache",
    "RecentSearch",
]
