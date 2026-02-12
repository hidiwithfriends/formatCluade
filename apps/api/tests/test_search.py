"""Tests for search API endpoints."""

import pytest
from uuid import uuid4
from datetime import date, time, datetime
from decimal import Decimal

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Event, Artist, RecentSearch
from app.models.event import EventCategory


@pytest.fixture
async def test_searchable_events(
    db_session: AsyncSession, test_artist: Artist
) -> list[Event]:
    """Create test events for search."""
    events = [
        Event(
            id=uuid4(),
            title="BTS World Tour 2026",
            category=EventCategory.CONCERT,
            artist_id=test_artist.id,
            artist_name="BTS",
            event_date=date(2026, 3, 15),
            event_time=time(18, 0),
            timezone="Asia/Seoul",
            venue="Seoul Olympic Stadium",
            city="Seoul",
            country="South Korea",
            source="ticketlink.co.kr",
            source_url="https://www.ticketlink.co.kr/product/12345",
            collected_at=datetime.utcnow(),
        ),
        Event(
            id=uuid4(),
            title="NewJeans Fan Meeting",
            category=EventCategory.FANMEETING,
            artist_id=test_artist.id,
            artist_name="NewJeans",
            event_date=date(2026, 4, 1),
            event_time=time(19, 0),
            timezone="Asia/Seoul",
            venue="KSPO Dome",
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
    return events


class TestRAGSearch:
    """Tests for POST /api/v1/search"""

    async def test_search_basic(
        self, client: AsyncClient, test_searchable_events: list[Event]
    ):
        """Test basic search."""
        response = await client.post(
            "/api/v1/search",
            json={"query": "BTS"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "searchId" in data
        assert data["query"] == "BTS"
        assert "events" in data
        assert "total" in data
        assert "searchTime" in data
        assert "cached" in data

    async def test_search_empty_query(self, client: AsyncClient):
        """Test search with empty query."""
        response = await client.post(
            "/api/v1/search",
            json={"query": ""},
        )
        assert response.status_code == 422  # Validation error

    async def test_search_with_pagination(
        self, client: AsyncClient, test_searchable_events: list[Event]
    ):
        """Test search with pagination."""
        response = await client.post(
            "/api/v1/search?page=1&per_page=1",
            json={"query": "Seoul"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["page"] == 1


class TestAutocomplete:
    """Tests for GET /api/v1/search/autocomplete"""

    async def test_autocomplete(self, client: AsyncClient, test_artist: Artist):
        """Test artist autocomplete."""
        response = await client.get("/api/v1/search/autocomplete?q=Test")
        assert response.status_code == 200
        data = response.json()
        assert "data" in data

    async def test_autocomplete_min_length(self, client: AsyncClient):
        """Test autocomplete with query too short."""
        response = await client.get("/api/v1/search/autocomplete?q=")
        assert response.status_code == 422  # Validation error


class TestRecentSearches:
    """Tests for recent searches endpoints."""

    async def test_get_recent_searches_empty(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Test getting recent searches when none exist."""
        response = await client.get("/api/v1/search/recent", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["data"] == []

    async def test_save_recent_search(self, client: AsyncClient, auth_headers: dict):
        """Test saving a recent search."""
        response = await client.post(
            "/api/v1/search/recent",
            json={"query": "BTS"},
            headers=auth_headers,
        )
        assert response.status_code == 201
        data = response.json()
        assert data["query"] == "BTS"
        assert "id" in data
        assert "searchedAt" in data

    async def test_get_recent_searches_after_save(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Test getting recent searches after saving some."""
        # Save a few searches
        await client.post(
            "/api/v1/search/recent",
            json={"query": "BTS"},
            headers=auth_headers,
        )
        await client.post(
            "/api/v1/search/recent",
            json={"query": "NewJeans"},
            headers=auth_headers,
        )

        response = await client.get("/api/v1/search/recent", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]) == 2
        # Should be ordered by most recent first
        assert data["data"][0]["query"] == "NewJeans"

    async def test_delete_recent_search(
        self,
        client: AsyncClient,
        auth_headers: dict,
    ):
        """Test deleting a specific recent search."""
        # First save a search
        save_response = await client.post(
            "/api/v1/search/recent",
            json={"query": "BTS"},
            headers=auth_headers,
        )
        search_id = save_response.json()["id"]

        # Delete it
        response = await client.delete(
            f"/api/v1/search/recent/{search_id}",
            headers=auth_headers,
        )
        assert response.status_code == 200

        # Verify it's gone
        get_response = await client.get("/api/v1/search/recent", headers=auth_headers)
        assert len(get_response.json()["data"]) == 0

    async def test_clear_recent_searches(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Test clearing all recent searches."""
        # Save a few searches
        await client.post(
            "/api/v1/search/recent",
            json={"query": "BTS"},
            headers=auth_headers,
        )
        await client.post(
            "/api/v1/search/recent",
            json={"query": "NewJeans"},
            headers=auth_headers,
        )

        # Clear all
        response = await client.delete("/api/v1/search/recent", headers=auth_headers)
        assert response.status_code == 200

        # Verify all are gone
        get_response = await client.get("/api/v1/search/recent", headers=auth_headers)
        assert len(get_response.json()["data"]) == 0

    async def test_recent_searches_unauthenticated(self, client: AsyncClient):
        """Test recent searches require authentication."""
        response = await client.get("/api/v1/search/recent")
        assert response.status_code == 403  # HTTPBearer returns 403 without token
