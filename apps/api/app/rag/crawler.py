"""Web crawler using Tavily API for event search."""

from typing import List, Optional
import httpx
from pydantic import BaseModel

from app.config import settings


class WebSearchResult(BaseModel):
    """Result from web search."""

    title: str
    url: str
    content: str
    score: float


class TavilyCrawler:
    """Web crawler using Tavily Search API."""

    BASE_URL = "https://api.tavily.com"

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.tavily_api_key

    async def search(
        self,
        query: str,
        max_results: int = 10,
        search_depth: str = "advanced",
        include_domains: Optional[List[str]] = None,
    ) -> List[WebSearchResult]:
        """
        Search the web for artist events.

        Args:
            query: Search query (e.g., "BTS 콘서트 2024")
            max_results: Maximum number of results
            search_depth: "basic" or "advanced"
            include_domains: Limit to specific domains

        Returns:
            List of search results with content
        """
        if not self.api_key:
            # Return empty results if no API key (for testing)
            return []

        async with httpx.AsyncClient(timeout=30.0) as client:
            payload = {
                "api_key": self.api_key,
                "query": f"{query} concert event schedule 콘서트 일정",
                "search_depth": search_depth,
                "max_results": max_results,
                "include_answer": False,
                "include_raw_content": False,
            }

            if include_domains:
                payload["include_domains"] = include_domains

            try:
                response = await client.post(
                    f"{self.BASE_URL}/search",
                    json=payload,
                )
                response.raise_for_status()
                data = response.json()

                results = []
                for item in data.get("results", []):
                    results.append(
                        WebSearchResult(
                            title=item.get("title", ""),
                            url=item.get("url", ""),
                            content=item.get("content", ""),
                            score=item.get("score", 0.0),
                        )
                    )
                return results

            except httpx.HTTPError as e:
                # Log error and return empty results
                print(f"Tavily API error: {e}")
                return []


# Singleton instance
crawler = TavilyCrawler()
