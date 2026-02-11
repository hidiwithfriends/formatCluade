"""Search-related models: SearchCache and RecentSearch."""

from typing import Optional, List
import uuid
from datetime import datetime

from sqlalchemy import String, Integer, ForeignKey, DateTime, func, JSON, Index
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID

from app.database import Base
from app.models.base import UUIDMixin


class SearchCache(Base, UUIDMixin):
    """Cache for RAG search results (24-hour TTL)."""

    __tablename__ = "search_caches"

    # Search query (normalized: lowercase, trimmed)
    query: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
        unique=True,
        index=True,
    )

    # Cached event IDs (JSON array)
    event_ids: Mapped[List[str]] = mapped_column(
        JSON,
        nullable=False,
    )

    # Stats
    total_results: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )
    search_time_seconds: Mapped[float] = mapped_column(
        nullable=False,
    )

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True,
    )

    def __repr__(self) -> str:
        return f"<SearchCache query='{self.query}'>"


class RecentSearch(Base, UUIDMixin):
    """User's recent search history."""

    __tablename__ = "recent_searches"

    # User relation
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Search query
    query: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
    )

    # Timestamp
    searched_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # Composite index for user's recent searches
    __table_args__ = (
        Index(
            "ix_recent_searches_user_searched",
            user_id,
            searched_at.desc(),
        ),
    )

    def __repr__(self) -> str:
        return f"<RecentSearch user_id={self.user_id} query='{self.query}'>"
