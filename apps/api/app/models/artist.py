from typing import TYPE_CHECKING, List, Optional
from sqlalchemy import String, Integer, ForeignKey, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime

from app.database import Base
from app.models.base import UUIDMixin, TimestampMixin

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.event import Event


class Artist(Base, UUIDMixin, TimestampMixin):
    """Artist model for music artists/groups."""

    __tablename__ = "artists"

    # Basic info
    name: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
        index=True,
    )
    name_ko: Mapped[Optional[str]] = mapped_column(
        String(200),
        nullable=True,
    )
    image_url: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
    )
    genre: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
    )

    # Stats
    follower_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    # Relationships
    followers: Mapped[List["User"]] = relationship(
        "User",
        secondary="user_artists",
        back_populates="followed_artists",
        lazy="selectin",
    )
    events: Mapped[List["Event"]] = relationship(
        "Event",
        back_populates="artist",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<Artist {self.name}>"


class UserArtist(Base):
    """Association table for User-Artist many-to-many relationship."""

    __tablename__ = "user_artists"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    artist_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("artists.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
