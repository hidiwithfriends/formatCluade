"""LLM-based event information extractor using OpenAI."""

from typing import List, Optional
from datetime import datetime, date, time
from decimal import Decimal
import json
from pydantic import BaseModel, Field
from openai import AsyncOpenAI

from app.config import settings
from app.models.event import EventCategory


class ExtractedEvent(BaseModel):
    """Event extracted by LLM from web content."""

    title: str
    artist_name: str
    category: EventCategory
    event_date: date
    event_time: Optional[time] = None
    venue: str
    address: Optional[str] = None
    city: str
    country: str
    timezone: str = "Asia/Seoul"
    price_currency: Optional[str] = None
    price_min: Optional[Decimal] = None
    price_max: Optional[Decimal] = None
    ticket_url: Optional[str] = None
    source_url: str
    confidence: float = Field(ge=0.0, le=1.0, description="Confidence score 0-1")


EXTRACTION_PROMPT = """You are an expert at extracting concert and event information from web content.
Extract all artist events (concerts, fanmeetings, broadcasts, festivals) from the following content.

For each event, extract:
- title: Event name
- artist_name: Artist/group name
- category: One of "concert", "fanmeeting", "broadcast", "festival"
- event_date: Date in YYYY-MM-DD format
- event_time: Time in HH:MM format (24-hour), if available
- venue: Venue name
- address: Full address, if available
- city: City name
- country: Country name
- timezone: Timezone (e.g., "Asia/Seoul", "Asia/Tokyo")
- price_currency: Currency code (e.g., "KRW", "JPY", "USD")
- price_min: Minimum ticket price (number only)
- price_max: Maximum ticket price (number only)
- ticket_url: Ticket purchase URL, if available
- source_url: The URL this information came from
- confidence: Your confidence in this extraction (0.0 to 1.0)

Only extract events that are clearly about the searched artist.
Skip events with unclear or incomplete information.
Return a JSON array of events.

Search query: {query}
Source URL: {source_url}

Content:
{content}

Return ONLY a valid JSON array. Example format:
[
  {{
    "title": "BTS World Tour",
    "artist_name": "BTS",
    "category": "concert",
    "event_date": "2024-03-15",
    "event_time": "18:00",
    "venue": "Seoul Olympic Stadium",
    "city": "Seoul",
    "country": "South Korea",
    "timezone": "Asia/Seoul",
    "price_currency": "KRW",
    "price_min": 110000,
    "price_max": 198000,
    "source_url": "https://example.com",
    "confidence": 0.9
  }}
]
"""


class EventExtractor:
    """Extract event information from web content using GPT-4."""

    def __init__(self, api_key: Optional[str] = None):
        self.client = AsyncOpenAI(api_key=api_key or settings.openai_api_key)

    async def extract_events(
        self,
        query: str,
        content: str,
        source_url: str,
    ) -> List[ExtractedEvent]:
        """
        Extract events from web content using LLM.

        Args:
            query: Original search query
            content: Web page content
            source_url: URL of the source

        Returns:
            List of extracted events
        """
        if not settings.openai_api_key:
            return []

        prompt = EXTRACTION_PROMPT.format(
            query=query,
            source_url=source_url,
            content=content[:8000],  # Limit content length
        )

        try:
            response = await self.client.chat.completions.create(
                model="gpt-4o-mini",  # Cost-effective for extraction
                messages=[
                    {
                        "role": "system",
                        "content": "You are an event extraction assistant. Always respond with valid JSON.",
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.1,
                response_format={"type": "json_object"},
            )

            content = response.choices[0].message.content
            if not content:
                return []

            # Parse JSON response
            data = json.loads(content)

            # Handle both array and object with array
            events_data = data if isinstance(data, list) else data.get("events", [])

            events = []
            for item in events_data:
                try:
                    # Parse date
                    event_date = datetime.strptime(
                        item["event_date"], "%Y-%m-%d"
                    ).date()

                    # Parse time if present
                    event_time = None
                    if item.get("event_time"):
                        try:
                            event_time = datetime.strptime(
                                item["event_time"], "%H:%M"
                            ).time()
                        except ValueError:
                            pass

                    # Create event
                    event = ExtractedEvent(
                        title=item["title"],
                        artist_name=item["artist_name"],
                        category=EventCategory(item["category"]),
                        event_date=event_date,
                        event_time=event_time,
                        venue=item["venue"],
                        address=item.get("address"),
                        city=item["city"],
                        country=item["country"],
                        timezone=item.get("timezone", "Asia/Seoul"),
                        price_currency=item.get("price_currency"),
                        price_min=(
                            Decimal(str(item["price_min"]))
                            if item.get("price_min")
                            else None
                        ),
                        price_max=(
                            Decimal(str(item["price_max"]))
                            if item.get("price_max")
                            else None
                        ),
                        ticket_url=item.get("ticket_url"),
                        source_url=source_url,
                        confidence=float(item.get("confidence", 0.5)),
                    )
                    events.append(event)
                except (KeyError, ValueError) as e:
                    print(f"Error parsing event: {e}")
                    continue

            return events

        except Exception as e:
            print(f"OpenAI extraction error: {e}")
            return []


# Singleton instance
extractor = EventExtractor()
