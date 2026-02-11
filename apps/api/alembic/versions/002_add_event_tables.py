"""Add event tables (events, event_embeddings, search_caches, recent_searches)

Revision ID: 002_add_events
Revises: 001_initial_auth
Create Date: 2024-01-02 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "002_add_events"
down_revision: Union[str, None] = "001_initial_auth"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Enable pgvector extension
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    # Create event category enum
    event_category_enum = postgresql.ENUM(
        "concert", "fanmeeting", "broadcast", "festival",
        name="eventcategory",
        create_type=True,
    )
    event_category_enum.create(op.get_bind(), checkfirst=True)

    # Create events table
    op.create_table(
        "events",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("title", sa.String(length=500), nullable=False),
        sa.Column(
            "category",
            postgresql.ENUM(
                "concert", "fanmeeting", "broadcast", "festival",
                name="eventcategory",
                create_type=False,
            ),
            nullable=False,
        ),
        sa.Column("artist_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("artist_name", sa.String(length=200), nullable=False),
        sa.Column("event_date", sa.Date(), nullable=False),
        sa.Column("event_time", sa.Time(), nullable=True),
        sa.Column("timezone", sa.String(length=50), nullable=False, server_default="Asia/Seoul"),
        sa.Column("venue", sa.String(length=300), nullable=False),
        sa.Column("address", sa.String(length=500), nullable=True),
        sa.Column("city", sa.String(length=100), nullable=False),
        sa.Column("country", sa.String(length=100), nullable=False),
        sa.Column("price_currency", sa.String(length=10), nullable=True),
        sa.Column("price_min", sa.Numeric(precision=12, scale=2), nullable=True),
        sa.Column("price_max", sa.Numeric(precision=12, scale=2), nullable=True),
        sa.Column("price_tiers", postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column("image_url", sa.String(length=500), nullable=True),
        sa.Column("ticket_url", sa.String(length=500), nullable=True),
        sa.Column("source", sa.String(length=200), nullable=False),
        sa.Column("source_url", sa.String(length=500), nullable=False),
        sa.Column("collected_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["artist_id"],
            ["artists.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_events_title"), "events", ["title"], unique=False)
    op.create_index(op.f("ix_events_category"), "events", ["category"], unique=False)
    op.create_index(op.f("ix_events_artist_id"), "events", ["artist_id"], unique=False)
    op.create_index(op.f("ix_events_event_date"), "events", ["event_date"], unique=False)
    op.create_index(op.f("ix_events_city"), "events", ["city"], unique=False)
    op.create_index(op.f("ix_events_country"), "events", ["country"], unique=False)

    # Create event_embeddings table
    op.create_table(
        "event_embeddings",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("event_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("embedding", sa.dialects.postgresql.ARRAY(sa.Float), nullable=False),
        sa.Column("embedded_text", sa.String(length=2000), nullable=False),
        sa.Column("model", sa.String(length=100), nullable=False, server_default="text-embedding-3-small"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["event_id"],
            ["events.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("event_id"),
    )
    op.create_index(op.f("ix_event_embeddings_event_id"), "event_embeddings", ["event_id"], unique=True)

    # Alter embedding column to vector type (pgvector)
    op.execute("""
        ALTER TABLE event_embeddings
        ALTER COLUMN embedding TYPE vector(1536)
        USING embedding::vector(1536)
    """)

    # Create IVFFlat index for vector similarity search
    op.execute("""
        CREATE INDEX ix_event_embeddings_embedding
        ON event_embeddings
        USING ivfflat (embedding vector_cosine_ops)
        WITH (lists = 100)
    """)

    # Create search_caches table
    op.create_table(
        "search_caches",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("query", sa.String(length=500), nullable=False),
        sa.Column("event_ids", postgresql.JSON(astext_type=sa.Text()), nullable=False),
        sa.Column("total_results", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("search_time_seconds", sa.Float(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("query"),
    )
    op.create_index(op.f("ix_search_caches_query"), "search_caches", ["query"], unique=True)
    op.create_index(op.f("ix_search_caches_expires_at"), "search_caches", ["expires_at"], unique=False)

    # Create recent_searches table
    op.create_table(
        "recent_searches",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("query", sa.String(length=500), nullable=False),
        sa.Column(
            "searched_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_recent_searches_user_id"), "recent_searches", ["user_id"], unique=False)
    op.create_index(
        "ix_recent_searches_user_searched",
        "recent_searches",
        ["user_id", sa.text("searched_at DESC")],
        unique=False,
    )


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_table("recent_searches")
    op.drop_table("search_caches")

    # Drop vector index first
    op.execute("DROP INDEX IF EXISTS ix_event_embeddings_embedding")
    op.drop_table("event_embeddings")
    op.drop_table("events")

    # Drop enum type
    event_category_enum = postgresql.ENUM(
        "concert", "fanmeeting", "broadcast", "festival",
        name="eventcategory",
    )
    event_category_enum.drop(op.get_bind(), checkfirst=True)

    # Note: We don't drop the vector extension as other tables might use it
