"""Tests for events API endpoints."""

import pytest
from uuid import uuid4
from datetime import date, time, datetime
from decimal import Decimal

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Event, Artist
from app.models.event import EventCategory


@pytest.fixture
async def test_events(db_session: AsyncSession, test_artist: Artist) -> list[Event]:
    """Create test events."""
    events = [
        Event(
            id=uuid4(),
            title="BTS World Tour",
            category=EventCategory.CONCERT,
            artist_id=test_artist.id,
            artist_name=test_artist.name,
            event_date=date(2026, 3, 15),
            event_time=time(18, 0),
            timezone="Asia/Seoul",
            venue="Seoul Olympic Stadium",
            city="Seoul",
            country="South Korea",
            price_currency="KRW",
            price_min=Decimal("110000"),
            price_max=Decimal("198000"),
            source="ticketlink.co.kr",
            source_url="https://www.ticketlink.co.kr/product/12345",
            collected_at=datetime.utcnow(),
        ),
        Event(
            id=uuid4(),
            title="Fan Meeting 2026",
            category=EventCategory.FANMEETING,
            artist_id=test_artist.id,
            artist_name=test_artist.name,
            event_date=date(2026, 4, 1),
            event_time=time(19, 0),
            timezone="Asia/Seoul",
            venue="YES24 Live Hall",
            city="Seoul",
            country="South Korea",
            source="melon.com",
            source_url="https://www.melon.com/ticket/12345",
            collected_at=datetime.utcnow(),
        ),
    ]

    for event in events:
        db_session.add(event)

    await db_session.commit()

    for event in events:
        await db_session.refresh(event)

    return events


class TestListEvents:
    """Tests for GET /api/v1/events"""

    async def test_list_events_empty(self, client: AsyncClient):
        """Test listing events when none exist."""
        response = await client.get("/api/v1/events")
        assert response.status_code == 200
        data = response.json()
        assert data["data"] == []
        assert data["total"] == 0

    async def test_list_events_with_data(
        self, client: AsyncClient, test_events: list[Event]
    ):
        """Test listing events with existing data."""
        response = await client.get("/api/v1/events")
        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]) == 2
        assert data["total"] == 2

    async def test_filter_by_category(
        self, client: AsyncClient, test_events: list[Event]
    ):
        """Test filtering events by category."""
        response = await client.get("/api/v1/events?category=concert")
        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]) == 1
        assert data["data"][0]["category"] == "concert"

    async def test_filter_by_city(self, client: AsyncClient, test_events: list[Event]):
        """Test filtering events by city."""
        response = await client.get("/api/v1/events?city=Seoul")
        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]) == 2

    async def test_pagination(self, client: AsyncClient, test_events: list[Event]):
        """Test pagination."""
        response = await client.get("/api/v1/events?page=1&per_page=1")
        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]) == 1
        assert data["has_more"] is True


class TestGetEvent:
    """Tests for GET /api/v1/events/{event_id}"""

    async def test_get_event(self, client: AsyncClient, test_events: list[Event]):
        """Test getting a single event."""
        event = test_events[0]
        response = await client.get(f"/api/v1/events/{event.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(event.id)
        assert data["title"] == event.title
        assert data["category"] == event.category.value

    async def test_get_event_not_found(self, client: AsyncClient):
        """Test getting a non-existent event."""
        response = await client.get(f"/api/v1/events/{uuid4()}")
        assert response.status_code == 404


class TestGetArtistEvents:
    """Tests for GET /api/v1/artists/{artist_id}/events"""

    async def test_get_artist_events(
        self, client: AsyncClient, test_artist: Artist, test_events: list[Event]
    ):
        """Test getting events for an artist."""
        response = await client.get(f"/api/v1/artists/{test_artist.id}/events")
        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]) == 2

    async def test_get_artist_events_not_found(self, client: AsyncClient):
        """Test getting events for non-existent artist."""
        response = await client.get(f"/api/v1/artists/{uuid4()}/events")
        assert response.status_code == 404
