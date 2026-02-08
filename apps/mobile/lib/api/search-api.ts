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

// ===== Real API Functions (to be implemented in Step 4) =====

const realSearchApi = {
  autocompleteArtists: async (query: string): Promise<Artist[]> => {
    return apiClient.get<Artist[]>("/api/v1/artists", {
      params: { q: query, limit: "10" },
    });
  },

  ragSearch: async (
    query: string,
    page: number = 1,
    pageSize: number = 20
  ): Promise<SearchResult> => {
    if (page === 1) {
      // Initial search - POST request
      return apiClient.post<SearchResult>("/api/v1/search", {
        query,
        page_size: pageSize,
      });
    }
    // Subsequent pages would use GET with search_id
    throw new Error("Pagination not implemented for real API yet");
  },

  getSearchPage: async (
    searchId: string,
    page: number,
    pageSize: number = 20
  ): Promise<{ events: Event[]; hasMore: boolean }> => {
    return apiClient.get(`/api/v1/search/${searchId}`, {
      params: { page: page.toString(), page_size: pageSize.toString() },
    });
  },

  getArtist: async (artistId: string): Promise<Artist | null> => {
    try {
      return await apiClient.get<Artist>(`/api/v1/artists/${artistId}`);
    } catch {
      return null;
    }
  },

  getArtistEvents: async (artistId: string): Promise<Event[]> => {
    return apiClient.get<Event[]>(`/api/v1/artists/${artistId}/events`);
  },

  getRelatedArtists: async (artistId: string): Promise<Artist[]> => {
    return apiClient.get<Artist[]>(`/api/v1/artists/${artistId}/related`);
  },

  getEvent: async (eventId: string): Promise<Event | null> => {
    try {
      return await apiClient.get<Event>(`/api/v1/events/${eventId}`);
    } catch {
      return null;
    }
  },

  getRecentSearches: async (): Promise<RecentSearch[]> => {
    return apiClient.get<RecentSearch[]>("/api/v1/users/me/recent-searches");
  },

  saveRecentSearch: async (query: string): Promise<void> => {
    await apiClient.post("/api/v1/users/me/recent-searches", { query });
  },

  deleteRecentSearch: async (searchId: string): Promise<void> => {
    await apiClient.delete(`/api/v1/users/me/recent-searches/${searchId}`);
  },

  clearRecentSearches: async (): Promise<void> => {
    await apiClient.delete("/api/v1/users/me/recent-searches");
  },

  getPopularArtists: async (): Promise<Artist[]> => {
    return apiClient.get<Artist[]>("/api/v1/artists/popular");
  },

  getFollowedArtists: async (): Promise<Artist[]> => {
    return apiClient.get<Artist[]>("/api/v1/users/me/artists");
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
