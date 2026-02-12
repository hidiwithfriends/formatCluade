"""OpenAI embeddings for vector search."""

from typing import List, Optional
from openai import AsyncOpenAI

from app.config import settings


class EmbeddingsService:
    """Generate embeddings using OpenAI API."""

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.client = AsyncOpenAI(api_key=api_key or settings.openai_api_key)
        self.model = model or settings.openai_embedding_model

    async def get_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for a single text.

        Args:
            text: Text to embed

        Returns:
            1536-dimensional embedding vector
        """
        if not settings.openai_api_key:
            # Return zero vector for testing
            return [0.0] * 1536

        # Clean and truncate text
        text = text.replace("\n", " ").strip()
        if len(text) > 8000:
            text = text[:8000]

        response = await self.client.embeddings.create(
            model=self.model,
            input=text,
        )

        return response.data[0].embedding

    async def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts.

        Args:
            texts: List of texts to embed

        Returns:
            List of 1536-dimensional embedding vectors
        """
        if not settings.openai_api_key:
            return [[0.0] * 1536 for _ in texts]

        # Clean and truncate texts
        cleaned_texts = []
        for text in texts:
            text = text.replace("\n", " ").strip()
            if len(text) > 8000:
                text = text[:8000]
            cleaned_texts.append(text)

        response = await self.client.embeddings.create(
            model=self.model,
            input=cleaned_texts,
        )

        return [item.embedding for item in response.data]

    def create_event_text(
        self,
        title: str,
        artist_name: str,
        category: str,
        venue: str,
        city: str,
        country: str,
    ) -> str:
        """
        Create text representation of an event for embedding.

        Args:
            title: Event title
            artist_name: Artist name
            category: Event category
            venue: Venue name
            city: City
            country: Country

        Returns:
            Text suitable for embedding
        """
        return f"{artist_name} {title} {category} at {venue}, {city}, {country}"


# Singleton instance
embeddings_service = EmbeddingsService()
