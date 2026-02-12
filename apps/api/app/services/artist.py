from typing import Optional, List, Tuple
from uuid import UUID
from sqlalchemy import select, or_, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Artist
from app.schemas import ArtistCreate, ArtistUpdate


class ArtistService:
    """Service for artist operations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_artist_by_id(self, artist_id: UUID) -> Optional[Artist]:
        """Get artist by ID."""
        result = await self.db.execute(
            select(Artist).where(Artist.id == artist_id)
        )
        return result.scalar_one_or_none()

    async def get_artist_by_name(self, name: str) -> Optional[Artist]:
        """Get artist by exact name."""
        result = await self.db.execute(
            select(Artist).where(Artist.name == name)
        )
        return result.scalar_one_or_none()

    async def create_artist(self, data: ArtistCreate) -> Artist:
        """Create a new artist."""
        artist = Artist(**data.model_dump())
        self.db.add(artist)
        await self.db.commit()
        await self.db.refresh(artist)
        return artist

    async def update_artist(self, artist: Artist, data: ArtistUpdate) -> Artist:
        """Update artist information."""
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(artist, field, value)
        await self.db.commit()
        await self.db.refresh(artist)
        return artist

    async def search_artists(
        self,
        query: str,
        page: int = 1,
        per_page: int = 20,
    ) -> Tuple[List[Artist], int]:
        """Search artists by name. Returns (artists, total_count)."""
        search_pattern = f"%{query}%"

        # Count total
        count_result = await self.db.execute(
            select(func.count(Artist.id)).where(
                or_(
                    Artist.name.ilike(search_pattern),
                    Artist.name_ko.ilike(search_pattern),
                )
            )
        )
        total = count_result.scalar() or 0

        # Get paginated results
        offset = (page - 1) * per_page
        result = await self.db.execute(
            select(Artist)
            .where(
                or_(
                    Artist.name.ilike(search_pattern),
                    Artist.name_ko.ilike(search_pattern),
                )
            )
            .order_by(Artist.follower_count.desc())
            .offset(offset)
            .limit(per_page)
        )
        artists = list(result.scalars().all())

        return artists, total

    async def get_popular_artists(
        self, page: int = 1, per_page: int = 20
    ) -> Tuple[List[Artist], int]:
        """Get popular artists ordered by follower count."""
        # Count total
        count_result = await self.db.execute(select(func.count(Artist.id)))
        total = count_result.scalar() or 0

        # Get paginated results
        offset = (page - 1) * per_page
        result = await self.db.execute(
            select(Artist)
            .order_by(Artist.follower_count.desc())
            .offset(offset)
            .limit(per_page)
        )
        artists = list(result.scalars().all())

        return artists, total

    async def get_or_create_artist(
        self, name: str, name_ko: Optional[str] = None, **kwargs
    ) -> Tuple[Artist, bool]:
        """Get existing artist or create new one. Returns (artist, is_new)."""
        artist = await self.get_artist_by_name(name)
        if artist:
            return artist, False

        data = ArtistCreate(name=name, name_ko=name_ko, **kwargs)
        artist = await self.create_artist(data)
        return artist, True

    async def get_related_artists(
        self,
        artist_id: UUID,
        genre: Optional[str] = None,
        limit: int = 6,
    ) -> List[Artist]:
        """Get artists related by genre, excluding the given artist."""
        if not genre:
            return []

        result = await self.db.execute(
            select(Artist)
            .where(
                Artist.id != artist_id,
                Artist.genre == genre,
            )
            .order_by(Artist.follower_count.desc())
            .limit(limit)
        )
        return list(result.scalars().all())
