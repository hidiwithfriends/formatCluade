"""RAG Pipeline: combines crawler, extractor, and embeddings."""

from typing import List, Tuple
from datetime import datetime
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.rag.crawler import crawler, WebSearchResult
from app.rag.extractor import extractor, ExtractedEvent
from app.rag.embeddings import embeddings_service
from app.models import Event, EventEmbedding, Artist
from app.services.artist import ArtistService


class RAGPipeline:
    """
    Complete RAG pipeline for event search.

    Flow:
    1. Web search (Tavily)
    2. LLM extraction (GPT-4)
    3. Embeddings generation (OpenAI)
    4. Store in database (PostgreSQL + pgvector)
    """

    def __init__(self, db: AsyncSession):
        self.db = db
        self.artist_service = ArtistService(db)

    async def search_and_extract(
        self,
        query: str,
        max_web_results: int = 10,
    ) -> List[ExtractedEvent]:
        """
        Search web and extract events.

        Args:
            query: Search query
            max_web_results: Max web search results

        Returns:
            List of extracted events
        """
        # Step 1: Web search
        web_results = await crawler.search(query, max_results=max_web_results)

        if not web_results:
            return []

        # Step 2: Extract events from each result
        all_events: List[ExtractedEvent] = []
        for result in web_results:
            events = await extractor.extract_events(
                query=query,
                content=result.content,
                source_url=result.url,
            )
            all_events.extend(events)

        # Deduplicate by title + date
        seen = set()
        unique_events = []
        for event in all_events:
            key = (event.title.lower(), event.event_date.isoformat())
            if key not in seen:
                seen.add(key)
                unique_events.append(event)

        return unique_events

    async def store_events(
        self,
        extracted_events: List[ExtractedEvent],
    ) -> List[Event]:
        """
        Store extracted events in database with embeddings.

        Args:
            extracted_events: Events extracted by LLM

        Returns:
            List of created Event models
        """
        stored_events: List[Event] = []

        for extracted in extracted_events:
            # Get or create artist
            artist, _ = await self.artist_service.get_or_create_artist(
                name=extracted.artist_name
            )

            # Create event
            event = Event(
                title=extracted.title,
                category=extracted.category,
                artist_id=artist.id,
                artist_name=extracted.artist_name,
                event_date=extracted.event_date,
                event_time=extracted.event_time,
                timezone=extracted.timezone,
                venue=extracted.venue,
                address=extracted.address,
                city=extracted.city,
                country=extracted.country,
                price_currency=extracted.price_currency,
                price_min=extracted.price_min,
                price_max=extracted.price_max,
                ticket_url=extracted.ticket_url,
                source=extracted.source_url.split("/")[2]
                if "/" in extracted.source_url
                else extracted.source_url,
                source_url=extracted.source_url,
                collected_at=datetime.utcnow(),
            )
            self.db.add(event)
            await self.db.flush()  # Get event.id

            # Generate embedding
            event_text = embeddings_service.create_event_text(
                title=extracted.title,
                artist_name=extracted.artist_name,
                category=extracted.category.value,
                venue=extracted.venue,
                city=extracted.city,
                country=extracted.country,
            )
            embedding_vector = await embeddings_service.get_embedding(event_text)

            # Store embedding
            event_embedding = EventEmbedding(
                event_id=event.id,
                embedding=embedding_vector,
                embedded_text=event_text[:2000],
                model=embeddings_service.model,
            )
            self.db.add(event_embedding)

            stored_events.append(event)

        await self.db.commit()
        return stored_events

    async def run(
        self,
        query: str,
        max_web_results: int = 10,
    ) -> Tuple[List[Event], float]:
        """
        Run complete RAG pipeline.

        Args:
            query: Search query
            max_web_results: Max web search results

        Returns:
            Tuple of (events, search_time_seconds)
        """
        import time

        start_time = time.time()

        # Extract events from web
        extracted_events = await self.search_and_extract(query, max_web_results)

        # Store events with embeddings
        events = await self.store_events(extracted_events)

        search_time = time.time() - start_time
        return events, search_time
