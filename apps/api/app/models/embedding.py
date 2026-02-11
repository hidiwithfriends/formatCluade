"""Event embedding model for vector search with pgvector."""

from typing import TYPE_CHECKING, Optional, List
import uuid
from datetime import datetime

from sqlalchemy import String, ForeignKey, DateTime, func, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from pgvector.sqlalchemy import Vector

from app.database import Base
from app.models.base import UUIDMixin

if TYPE_CHECKING:
    from app.models.event import Event


# OpenAI text-embedding-3-small produces 1536-dimensional vectors
EMBEDDING_DIMENSION = 1536


class EventEmbedding(Base, UUIDMixin):
    """Event embedding for vector similarity search."""

    __tablename__ = "event_embeddings"

    # Event relation (one-to-one)
    event_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("events.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )

    # Embedding vector (1536 dimensions for text-embedding-3-small)
    embedding: Mapped[List[float]] = mapped_column(
        Vector(EMBEDDING_DIMENSION),
        nullable=False,
    )

    # Text that was embedded (for debugging/audit)
    embedded_text: Mapped[str] = mapped_column(
        String(2000),
        nullable=False,
    )

    # Model info
    model: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        default="text-embedding-3-small",
    )

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # Relationships
    event: Mapped["Event"] = relationship(
        "Event",
        back_populates="embedding",
        lazy="selectin",
    )

    # Indexes for vector similarity search
    __table_args__ = (
        # IVFFlat index for approximate nearest neighbor search
        # lists = sqrt(num_rows) is a good starting point
        Index(
            "ix_event_embeddings_embedding",
            embedding,
            postgresql_using="ivfflat",
            postgresql_with={"lists": 100},
            postgresql_ops={"embedding": "vector_cosine_ops"},
        ),
    )

    def __repr__(self) -> str:
        return f"<EventEmbedding event_id={self.event_id}>"
