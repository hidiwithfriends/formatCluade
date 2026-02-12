"""Event service for database operations."""

from typing import Optional, List, Tuple
from uuid import UUID
from datetime import date

from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import Event, EventEmbedding, Artist
from app.models.event import EventCategory


class EventService:
    """Service for event operations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_event_by_id(self, event_id: UUID) -> Optional[Event]:
        """Get event by ID with artist."""
        result = await self.db.execute(
            select(Event)
            .options(selectinload(Event.artist))
            .where(Event.id == event_id)
        )
        return result.scalar_one_or_none()

    async def get_events_by_artist(
        self,
        artist_id: UUID,
        include_past: bool = False,
        page: int = 1,
        per_page: int = 20,
    ) -> Tuple[List[Event], int]:
        """Get events for an artist."""
        # Build base query
        conditions = [Event.artist_id == artist_id]
        if not include_past:
            conditions.append(Event.event_date >= date.today())

        # Count total
        count_result = await self.db.execute(
            select(func.count(Event.id)).where(and_(*conditions))
        )
        total = count_result.scalar() or 0

        # Get paginated results
        offset = (page - 1) * per_page
        result = await self.db.execute(
            select(Event)
            .where(and_(*conditions))
            .order_by(Event.event_date.asc(), Event.event_time.asc())
            .offset(offset)
            .limit(per_page)
        )
        events = list(result.scalars().all())

        return events, total

    async def get_events_by_ids(self, event_ids: List[UUID]) -> List[Event]:
        """Get multiple events by their IDs."""
        if not event_ids:
            return []

        result = await self.db.execute(
            select(Event).where(Event.id.in_(event_ids))
        )
        return list(result.scalars().all())

    async def search_events(
        self,
        query: str,
        category: Optional[EventCategory] = None,
        city: Optional[str] = None,
        country: Optional[str] = None,
        from_date: Optional[date] = None,
        to_date: Optional[date] = None,
        page: int = 1,
        per_page: int = 20,
    ) -> Tuple[List[Event], int]:
        """Search events by text and filters."""
        conditions = []

        # Text search
        if query:
            search_pattern = f"%{query}%"
            conditions.append(
                Event.title.ilike(search_pattern)
                | Event.artist_name.ilike(search_pattern)
                | Event.venue.ilike(search_pattern)
            )

        # Filters
        if category:
            conditions.append(Event.category == category)
        if city:
            conditions.append(Event.city.ilike(f"%{city}%"))
        if country:
            conditions.append(Event.country.ilike(f"%{country}%"))
        if from_date:
            conditions.append(Event.event_date >= from_date)
        if to_date:
            conditions.append(Event.event_date <= to_date)

        # Default: only future events
        if not from_date:
            conditions.append(Event.event_date >= date.today())

        # Count total
        where_clause = and_(*conditions) if conditions else True
        count_result = await self.db.execute(
            select(func.count(Event.id)).where(where_clause)
        )
        total = count_result.scalar() or 0

        # Get paginated results
        offset = (page - 1) * per_page
        result = await self.db.execute(
            select(Event)
            .where(where_clause)
            .order_by(Event.event_date.asc(), Event.event_time.asc())
            .offset(offset)
            .limit(per_page)
        )
        events = list(result.scalars().all())

        return events, total

    async def vector_search(
        self,
        query_embedding: List[float],
        limit: int = 20,
        include_past: bool = False,
    ) -> List[Tuple[Event, float]]:
        """
        Search events by vector similarity.

        Args:
            query_embedding: Query embedding vector
            limit: Max results
            include_past: Include past events

        Returns:
            List of (event, distance) tuples, ordered by similarity
        """
        # Build query with vector similarity
        conditions = []
        if not include_past:
            conditions.append(Event.event_date >= date.today())

        # Note: This uses pgvector's <=> operator for cosine distance
        # Lower distance = more similar
        where_clause = and_(*conditions) if conditions else True

        # Raw SQL for vector search (SQLAlchemy doesn't have native pgvector support)
        from sqlalchemy import text

        sql = text("""
            SELECT e.*, ee.embedding <=> :embedding AS distance
            FROM events e
            JOIN event_embeddings ee ON e.id = ee.event_id
            WHERE e.event_date >= :today
            ORDER BY ee.embedding <=> :embedding
            LIMIT :limit
        """)

        result = await self.db.execute(
            sql,
            {
                "embedding": str(query_embedding),
                "today": date.today().isoformat(),
                "limit": limit,
            },
        )

        # This returns raw rows, need to convert to Event objects
        rows = result.fetchall()

        # Get event IDs from results
        event_ids = [row[0] for row in rows]  # Assuming id is first column
        distances = {row[0]: row[-1] for row in rows}  # id -> distance

        # Fetch full Event objects
        events = await self.get_events_by_ids(event_ids)
        event_map = {e.id: e for e in events}

        # Return in order with distances
        return [
            (event_map[eid], distances[eid])
            for eid in event_ids
            if eid in event_map
        ]

    async def create_event(self, **kwargs) -> Event:
        """Create a new event."""
        event = Event(**kwargs)
        self.db.add(event)
        await self.db.commit()
        await self.db.refresh(event)
        return event

    async def update_event(self, event: Event, **kwargs) -> Event:
        """Update an event."""
        for key, value in kwargs.items():
            if hasattr(event, key):
                setattr(event, key, value)
        await self.db.commit()
        await self.db.refresh(event)
        return event

    async def delete_event(self, event: Event) -> None:
        """Delete an event."""
        await self.db.delete(event)
        await self.db.commit()
