// API Client for F2: Artist Search & RAG
// Uses Mock Provider pattern for Mock/Real API switching

import { apiClient } from "./client";
import {
  mockSearchService,
  type Event,
  type SearchResult,
  type RecentSearch,
} from "../mocks/search-rag";
import type { Artist } from "../mocks/auth";

// Check if we should use mock API
const useMock = process.env.EXPO_PUBLIC_USE_MOCK_API !== "false";

// ===== API Response Types =====

interface ArtistListResponse {
  data: Artist[];
  total: number;
  page: number;
  per_page: number;
}

interface EventListResponse {
  data: Event[];
  total: number;
  page: number;
  per_page: number;
  has_more: boolean;
}

interface RecentSearchListResponse {
  data: RecentSearch[];
}

// ===== Real API Functions =====

const realSearchApi = {
  autocompleteArtists: async (query: string): Promise<Artist[]> => {
    const response = await apiClient.get<{ data: Artist[] }>(
      "/api/v1/search/autocomplete",
      {
        params: { q: query, limit: "10" },
      }
    );
    return response.data;
  },

  ragSearch: async (
    query: string,
    page: number = 1,
    pageSize: number = 20
  ): Promise<SearchResult> => {
    // POST request with query params for pagination
    return apiClient.post<SearchResult>(
      `/api/v1/search?page=${page}&per_page=${pageSize}`,
      { query }
    );
  },

  getSearchPage: async (
    searchId: string,
    page: number,
    pageSize: number = 20
  ): Promise<{ events: Event[]; hasMore: boolean }> => {
    // For real API, we just do another search
    // The cache on backend handles deduplication
    const result = await realSearchApi.ragSearch("", page, pageSize);
    return { events: result.events, hasMore: result.hasMore };
  },

  getArtist: async (artistId: string): Promise<Artist | null> => {
    try {
      return await apiClient.get<Artist>(`/api/v1/artists/${artistId}`);
    } catch {
      return null;
    }
  },

  getArtistEvents: async (artistId: string): Promise<Event[]> => {
    const response = await apiClient.get<EventListResponse>(
      `/api/v1/artists/${artistId}/events`
    );
    return response.data;
  },

  getRelatedArtists: async (artistId: string): Promise<Artist[]> => {
    const response = await apiClient.get<ArtistListResponse>(
      `/api/v1/artists/${artistId}/related`
    );
    return response.data;
  },

  getEvent: async (eventId: string): Promise<Event | null> => {
    try {
      return await apiClient.get<Event>(`/api/v1/events/${eventId}`);
    } catch {
      return null;
    }
  },

  getRecentSearches: async (): Promise<RecentSearch[]> => {
    const response = await apiClient.get<RecentSearchListResponse>(
      "/api/v1/search/recent"
    );
    return response.data;
  },

  saveRecentSearch: async (query: string): Promise<void> => {
    await apiClient.post("/api/v1/search/recent", { query });
  },

  deleteRecentSearch: async (searchId: string): Promise<void> => {
    await apiClient.delete(`/api/v1/search/recent/${searchId}`);
  },

  clearRecentSearches: async (): Promise<void> => {
    await apiClient.delete("/api/v1/search/recent");
  },

  getPopularArtists: async (): Promise<Artist[]> => {
    const response = await apiClient.get<ArtistListResponse>("/api/v1/artists");
    return response.data;
  },

  getFollowedArtists: async (): Promise<Artist[]> => {
    const response = await apiClient.get<ArtistListResponse>(
      "/api/v1/users/me/artists"
    );
    return response.data;
  },
};

// ===== Mock API Functions =====

const mockSearchApi = {
  autocompleteArtists: mockSearchService.autocompleteArtists,
  ragSearch: mockSearchService.ragSearch,
  getSearchPage: mockSearchService.getSearchPage,
  getArtist: mockSearchService.getArtist,
  getArtistEvents: mockSearchService.getArtistEvents,
  getRelatedArtists: mockSearchService.getRelatedArtists,
  getEvent: mockSearchService.getEvent,
  getRecentSearches: mockSearchService.getRecentSearches,
  saveRecentSearch: mockSearchService.saveRecentSearch,
  deleteRecentSearch: mockSearchService.deleteRecentSearch,
  clearRecentSearches: mockSearchService.clearRecentSearches,
  getPopularArtists: mockSearchService.getPopularArtists,
  getFollowedArtists: mockSearchService.getFollowedArtists,
};

// ===== Exported API (Mock Provider Pattern) =====

export const searchApi = useMock ? mockSearchApi : realSearchApi;

// Re-export types for convenience
export type { Event, SearchResult, RecentSearch } from "../mocks/search-rag";
export { categoryLabels, categoryColors } from "../mocks/search-rag";
