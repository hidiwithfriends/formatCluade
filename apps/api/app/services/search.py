"""Search service for RAG search and caching."""

from typing import Optional, List, Tuple
from uuid import UUID, uuid4
from datetime import datetime, timedelta
import time

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models import Event, SearchCache
from app.services.event import EventService
from app.rag import RAGPipeline, embeddings_service
from app.schemas import EventResponse


class SearchService:
    """Service for RAG search operations with caching."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.event_service = EventService(db)
        self.rag_pipeline = RAGPipeline(db)

    async def get_cached_search(self, query: str) -> Optional[SearchCache]:
        """Get cached search result if not expired."""
        normalized_query = query.lower().strip()

        result = await self.db.execute(
            select(SearchCache).where(
                SearchCache.query == normalized_query,
                SearchCache.expires_at > datetime.utcnow(),
            )
        )
        return result.scalar_one_or_none()

    async def save_search_cache(
        self,
        query: str,
        event_ids: List[UUID],
        search_time_seconds: float,
    ) -> SearchCache:
        """Save search results to cache."""
        normalized_query = query.lower().strip()

        # Delete existing cache for this query
        await self.db.execute(
            delete(SearchCache).where(SearchCache.query == normalized_query)
        )

        # Create new cache entry
        cache = SearchCache(
            query=normalized_query,
            event_ids=[str(eid) for eid in event_ids],
            total_results=len(event_ids),
            search_time_seconds=search_time_seconds,
            expires_at=datetime.utcnow()
            + timedelta(hours=settings.search_cache_ttl_hours),
        )
        self.db.add(cache)
        await self.db.commit()
        await self.db.refresh(cache)
        return cache

    async def rag_search(
        self,
        query: str,
        force_refresh: bool = False,
        page: int = 1,
        per_page: int = 20,
    ) -> Tuple[List[Event], str, int, float, bool]:
        """
        Perform RAG search with caching.

        Args:
            query: Search query
            force_refresh: Bypass cache
            page: Page number
            per_page: Items per page

        Returns:
            Tuple of (events, search_id, total, search_time, cached)
        """
        start_time = time.time()
        search_id = str(uuid4())

        # Check cache first
        cached = None
        if not force_refresh:
            cached = await self.get_cached_search(query)

        if cached:
            # Cache hit - return cached results
            event_ids = [UUID(eid) for eid in cached.event_ids]
            all_events = await self.event_service.get_events_by_ids(event_ids)

            # Paginate
            start_idx = (page - 1) * per_page
            end_idx = start_idx + per_page
            events = all_events[start_idx:end_idx]

            search_time = time.time() - start_time
            return events, search_id, len(event_ids), search_time, True

        # Cache miss - run RAG pipeline
        new_events, rag_time = await self.rag_pipeline.run(query)

        # Also search existing events by text
        existing_events, _ = await self.event_service.search_events(
            query=query, page=1, per_page=100
        )

        # Combine and deduplicate
        all_event_ids = set()
        combined_events = []
        for event in new_events + existing_events:
            if event.id not in all_event_ids:
                all_event_ids.add(event.id)
                combined_events.append(event)

        # Sort by date
        combined_events.sort(key=lambda e: (e.event_date, e.event_time or "00:00"))

        # Save to cache
        event_ids = [e.id for e in combined_events]
        search_time = time.time() - start_time
        await self.save_search_cache(query, event_ids, search_time)

        # Paginate
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        events = combined_events[start_idx:end_idx]

        return events, search_id, len(combined_events), search_time, False

    async def vector_search(
        self,
        query: str,
        limit: int = 20,
    ) -> List[Tuple[Event, float]]:
        """
        Perform vector similarity search.

        Args:
            query: Search query
            limit: Max results

        Returns:
            List of (event, distance) tuples
        """
        # Generate query embedding
        query_embedding = await embeddings_service.get_embedding(query)

        # Vector search
        return await self.event_service.vector_search(query_embedding, limit)

    async def cleanup_expired_cache(self) -> int:
        """Delete expired cache entries. Returns count of deleted entries."""
        result = await self.db.execute(
            delete(SearchCache).where(SearchCache.expires_at < datetime.utcnow())
        )
        await self.db.commit()
        return result.rowcount
