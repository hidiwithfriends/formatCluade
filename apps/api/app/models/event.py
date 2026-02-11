"""Event model for concerts, fanmeetings, broadcasts, and festivals."""

from typing import TYPE_CHECKING, Optional, List
from enum import Enum as PyEnum
from decimal import Decimal
import uuid
from datetime import datetime, date, time

from sqlalchemy import (
    String,
    Integer,
    Text,
    Date,
    Time,
    ForeignKey,
    Numeric,
    Enum,
    JSON,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from app.database import Base
from app.models.base import UUIDMixin, TimestampMixin

if TYPE_CHECKING:
    from app.models.artist import Artist


class EventCategory(str, PyEnum):
    """Event category enum."""

    CONCERT = "concert"
    FANMEETING = "fanmeeting"
    BROADCAST = "broadcast"
    FESTIVAL = "festival"


class Event(Base, UUIDMixin, TimestampMixin):
    """Event model for artist events."""

    __tablename__ = "events"

    # Basic info
    title: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
        index=True,
    )
    category: Mapped[EventCategory] = mapped_column(
        Enum(EventCategory, name="eventcategory", create_type=True),
        nullable=False,
        index=True,
    )

    # Artist relation
    artist_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("artists.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    artist_name: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )

    # Date and time
    event_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        index=True,
    )
    event_time: Mapped[Optional[time]] = mapped_column(
        Time,
        nullable=True,
    )
    timezone: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="Asia/Seoul",
    )

    # Location
    venue: Mapped[str] = mapped_column(
        String(300),
        nullable=False,
    )
    address: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
    )
    city: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
    )
    country: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
    )

    # Price info (stored as JSON for flexibility)
    price_currency: Mapped[Optional[str]] = mapped_column(
        String(10),
        nullable=True,
    )
    price_min: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(12, 2),
        nullable=True,
    )
    price_max: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(12, 2),
        nullable=True,
    )
    price_tiers: Mapped[Optional[dict]] = mapped_column(
        JSON,
        nullable=True,
    )

    # Media
    image_url: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
    )

    # Ticket info
    ticket_url: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
    )

    # Source info (RAG)
    source: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )
    source_url: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
    )
    collected_at: Mapped[datetime] = mapped_column(
        nullable=False,
    )

    # Relationships
    artist: Mapped["Artist"] = relationship(
        "Artist",
        back_populates="events",
        lazy="selectin",
    )
    embedding: Mapped[Optional["EventEmbedding"]] = relationship(
        "EventEmbedding",
        back_populates="event",
        uselist=False,
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<Event {self.title} ({self.event_date})>"


# Import here to avoid circular import
from app.models.embedding import EventEmbedding  # noqa: E402, F401
