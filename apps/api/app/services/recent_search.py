"""Recent search service for user search history."""

from typing import Optional, List
from uuid import UUID

from sqlalchemy import select, delete, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import RecentSearch


class RecentSearchService:
    """Service for managing user's recent search history."""

    MAX_RECENT_SEARCHES = 10

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_recent_searches(
        self,
        user_id: UUID,
        limit: int = 10,
    ) -> List[RecentSearch]:
        """Get user's recent searches, ordered by most recent first."""
        result = await self.db.execute(
            select(RecentSearch)
            .where(RecentSearch.user_id == user_id)
            .order_by(RecentSearch.searched_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def save_recent_search(
        self,
        user_id: UUID,
        query: str,
    ) -> RecentSearch:
        """
        Save a search query to user's history.

        If the query already exists, update its timestamp.
        Keeps only the most recent MAX_RECENT_SEARCHES entries.
        """
        normalized_query = query.strip()

        # Check if query already exists
        result = await self.db.execute(
            select(RecentSearch).where(
                RecentSearch.user_id == user_id,
                func.lower(RecentSearch.query) == normalized_query.lower(),
            )
        )
        existing = result.scalar_one_or_none()

        if existing:
            # Update timestamp by deleting and re-creating
            await self.db.delete(existing)
            await self.db.flush()

        # Create new entry
        recent_search = RecentSearch(
            user_id=user_id,
            query=normalized_query,
        )
        self.db.add(recent_search)
        await self.db.flush()

        # Cleanup old entries if over limit
        await self._cleanup_old_searches(user_id)

        await self.db.commit()
        await self.db.refresh(recent_search)
        return recent_search

    async def delete_recent_search(
        self,
        user_id: UUID,
        search_id: UUID,
    ) -> bool:
        """Delete a specific search from history. Returns True if deleted."""
        result = await self.db.execute(
            select(RecentSearch).where(
                RecentSearch.id == search_id,
                RecentSearch.user_id == user_id,
            )
        )
        search = result.scalar_one_or_none()

        if search:
            await self.db.delete(search)
            await self.db.commit()
            return True
        return False

    async def clear_recent_searches(self, user_id: UUID) -> int:
        """Clear all recent searches for user. Returns count of deleted."""
        result = await self.db.execute(
            delete(RecentSearch).where(RecentSearch.user_id == user_id)
        )
        await self.db.commit()
        return result.rowcount

    async def _cleanup_old_searches(self, user_id: UUID) -> None:
        """Keep only the most recent MAX_RECENT_SEARCHES entries."""
        # Get IDs to keep
        keep_result = await self.db.execute(
            select(RecentSearch.id)
            .where(RecentSearch.user_id == user_id)
            .order_by(RecentSearch.searched_at.desc())
            .limit(self.MAX_RECENT_SEARCHES)
        )
        keep_ids = [row[0] for row in keep_result.fetchall()]

        if not keep_ids:
            return

        # Delete entries not in keep list
        await self.db.execute(
            delete(RecentSearch).where(
                RecentSearch.user_id == user_id,
                RecentSearch.id.not_in(keep_ids),
            )
        )
