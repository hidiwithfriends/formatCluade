"""Event schemas for API request/response."""

from datetime import datetime, date, time
from decimal import Decimal
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel, Field

from app.models.event import EventCategory


# ============== Price Schemas ==============


class PriceTier(BaseModel):
    """Individual price tier."""

    name: str
    price: Decimal


class PriceInfo(BaseModel):
    """Price information for an event."""

    currency: str = Field(..., max_length=10)
    min: Decimal
    max: Decimal
    tiers: Optional[List[PriceTier]] = None


# ============== Event Schemas ==============


class EventBase(BaseModel):
    """Base event schema with common fields."""

    title: str = Field(..., min_length=1, max_length=500)
    category: EventCategory
    artist_name: str = Field(..., max_length=200)
    event_date: date
    event_time: Optional[time] = None
    timezone: str = Field(default="Asia/Seoul", max_length=50)
    venue: str = Field(..., max_length=300)
    address: Optional[str] = Field(None, max_length=500)
    city: str = Field(..., max_length=100)
    country: str = Field(..., max_length=100)


class EventCreate(EventBase):
    """Schema for creating an event."""

    artist_id: UUID
    price_currency: Optional[str] = None
    price_min: Optional[Decimal] = None
    price_max: Optional[Decimal] = None
    price_tiers: Optional[List[PriceTier]] = None
    image_url: Optional[str] = None
    ticket_url: Optional[str] = None
    source: str = Field(..., max_length=200)
    source_url: str = Field(..., max_length=500)
    collected_at: datetime


class EventUpdate(BaseModel):
    """Schema for updating an event."""

    title: Optional[str] = Field(None, max_length=500)
    category: Optional[EventCategory] = None
    event_date: Optional[date] = None
    event_time: Optional[time] = None
    venue: Optional[str] = Field(None, max_length=300)
    address: Optional[str] = Field(None, max_length=500)
    city: Optional[str] = Field(None, max_length=100)
    country: Optional[str] = Field(None, max_length=100)
    price_currency: Optional[str] = None
    price_min: Optional[Decimal] = None
    price_max: Optional[Decimal] = None
    price_tiers: Optional[List[PriceTier]] = None
    image_url: Optional[str] = None
    ticket_url: Optional[str] = None


# ============== Response Schemas ==============


class EventResponse(BaseModel):
    """Schema for event response (matches frontend Event type)."""

    id: UUID
    title: str
    artistId: UUID
    artistName: str
    category: EventCategory
    date: str  # ISO 8601 format
    time: str  # "HH:MM" format
    venue: str
    address: Optional[str] = None
    city: str
    country: str
    timezone: str
    price: Optional[PriceInfo] = None
    imageUrl: Optional[str] = None
    ticketUrl: Optional[str] = None
    source: str
    sourceUrl: str
    collectedAt: str  # ISO 8601 format

    class Config:
        from_attributes = True

    @classmethod
    def from_db_model(cls, event) -> "EventResponse":
        """Convert DB model to response schema."""
        price = None
        if event.price_currency and event.price_min is not None:
            tiers = None
            if event.price_tiers:
                tiers = [PriceTier(**t) for t in event.price_tiers]
            price = PriceInfo(
                currency=event.price_currency,
                min=event.price_min,
                max=event.price_max or event.price_min,
                tiers=tiers,
            )

        return cls(
            id=event.id,
            title=event.title,
            artistId=event.artist_id,
            artistName=event.artist_name,
            category=event.category,
            date=event.event_date.isoformat(),
            time=event.event_time.strftime("%H:%M") if event.event_time else "00:00",
            venue=event.venue,
            address=event.address,
            city=event.city,
            country=event.country,
            timezone=event.timezone,
            price=price,
            imageUrl=event.image_url,
            ticketUrl=event.ticket_url,
            source=event.source,
            sourceUrl=event.source_url,
            collectedAt=event.collected_at.isoformat(),
        )


class EventListResponse(BaseModel):
    """Schema for event list response."""

    data: List[EventResponse]
    total: int
    page: int = 1
    per_page: int = 20
    has_more: bool = False
