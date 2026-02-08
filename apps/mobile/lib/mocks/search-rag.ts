// Mock data for F2: Artist Search & RAG

import { Artist, mockPopularArtists, mockFollowedArtists } from "./auth";

// ===== Types =====

export type EventCategory = "concert" | "fanmeeting" | "broadcast" | "festival";

export interface Event {
  id: string;
  title: string;
  artistId: string;
  artistName: string;
  category: EventCategory;
  date: string; // ISO 8601 format
  time: string; // e.g., "18:00"
  venue: string;
  address: string;
  city: string;
  country: string;
  timezone: string;
  price?: {
    currency: string;
    min: number;
    max: number;
    tiers?: { name: string; price: number }[];
  };
  imageUrl?: string;
  ticketUrl?: string;
  source: string;
  sourceUrl: string;
  collectedAt: string;
}

export interface SearchResult {
  searchId: string;
  query: string;
  events: Event[];
  total: number;
  searchTime: number; // in seconds
  cached: boolean;
  page: number;
  hasMore: boolean;
}

export interface RecentSearch {
  id: string;
  query: string;
  searchedAt: string;
}

// ===== Mock Data =====

// Extended artist list for search
export const mockArtistsForSearch: Artist[] = [
  ...mockPopularArtists,
  {
    id: "artist-10",
    name: "LE SSERAFIM",
    nameKo: "르세라핌",
    imageUrl: "https://api.dicebear.com/7.x/shapes/png?seed=lesserafim",
    genre: "K-POP",
    followerCount: 15000000,
  },
  {
    id: "artist-11",
    name: "ATEEZ",
    nameKo: "에이티즈",
    imageUrl: "https://api.dicebear.com/7.x/shapes/png?seed=ateez",
    genre: "K-POP",
    followerCount: 12000000,
  },
  {
    id: "artist-12",
    name: "TWICE",
    nameKo: "트와이스",
    imageUrl: "https://api.dicebear.com/7.x/shapes/png?seed=twice",
    genre: "K-POP",
    followerCount: 35000000,
  },
];

// Hardcoded popular artists for MVP
export const mockHardcodedPopularArtists: Artist[] = [
  mockPopularArtists[2], // NewJeans
  mockPopularArtists[4], // aespa
  mockPopularArtists[5], // SEVENTEEN
  mockArtistsForSearch[9], // LE SSERAFIM
  mockArtistsForSearch[10], // ATEEZ
  mockPopularArtists[6], // Stray Kids
];

// Mock events data
export const mockEvents: Event[] = [
  // BTS events
  {
    id: "event-1",
    title: "BTS WORLD TOUR [PERMISSION TO DANCE]",
    artistId: "artist-1",
    artistName: "BTS",
    category: "concert",
    date: "2026-03-15",
    time: "18:00",
    venue: "서울 올림픽 체조경기장",
    address: "서울특별시 송파구 올림픽로 424",
    city: "서울",
    country: "대한민국",
    timezone: "Asia/Seoul",
    price: {
      currency: "KRW",
      min: 110000,
      max: 198000,
      tiers: [
        { name: "VIP", price: 198000 },
        { name: "R석", price: 154000 },
        { name: "S석", price: 110000 },
      ],
    },
    imageUrl: "https://picsum.photos/seed/bts-concert/400/300",
    ticketUrl: "https://tickets.example.com/bts-world-tour",
    source: "ticketlink.co.kr",
    sourceUrl: "https://www.ticketlink.co.kr/product/12345",
    collectedAt: "2026-02-05T10:30:00Z",
  },
  {
    id: "event-2",
    title: "BTS 지민 Solo Fan Meeting",
    artistId: "artist-1",
    artistName: "BTS",
    category: "fanmeeting",
    date: "2026-04-01",
    time: "19:00",
    venue: "YES24 라이브홀",
    address: "서울특별시 광진구 능동로 130",
    city: "서울",
    country: "대한민국",
    timezone: "Asia/Seoul",
    price: {
      currency: "KRW",
      min: 88000,
      max: 132000,
    },
    source: "melon.com",
    sourceUrl: "https://www.melon.com/ticket/12345",
    collectedAt: "2026-02-05T10:30:00Z",
  },
  {
    id: "event-3",
    title: "BTS 정국 - SBS 인기가요",
    artistId: "artist-1",
    artistName: "BTS",
    category: "broadcast",
    date: "2026-03-20",
    time: "15:40",
    venue: "SBS 프리즘타워",
    address: "서울특별시 마포구 상암산로 82",
    city: "서울",
    country: "대한민국",
    timezone: "Asia/Seoul",
    source: "sbs.co.kr",
    sourceUrl: "https://www.sbs.co.kr/inkigayo",
    collectedAt: "2026-02-05T10:30:00Z",
  },
  // NewJeans events
  {
    id: "event-4",
    title: "NewJeans Fan Meeting 'Bunnies Day'",
    artistId: "artist-3",
    artistName: "NewJeans",
    category: "fanmeeting",
    date: "2026-03-22",
    time: "17:00",
    venue: "KSPO DOME",
    address: "서울특별시 송파구 올림픽로 25",
    city: "서울",
    country: "대한민국",
    timezone: "Asia/Seoul",
    price: {
      currency: "KRW",
      min: 99000,
      max: 165000,
    },
    imageUrl: "https://picsum.photos/seed/nj-fanmeeting/400/300",
    ticketUrl: "https://tickets.example.com/newjeans-bunnies",
    source: "interpark.com",
    sourceUrl: "https://tickets.interpark.com/12345",
    collectedAt: "2026-02-06T14:20:00Z",
  },
  {
    id: "event-5",
    title: "NewJeans 1st World Tour 'Get Up'",
    artistId: "artist-3",
    artistName: "NewJeans",
    category: "concert",
    date: "2026-04-15",
    time: "19:00",
    venue: "도쿄돔",
    address: "1-3-61 Koraku, Bunkyo City, Tokyo",
    city: "도쿄",
    country: "일본",
    timezone: "Asia/Tokyo",
    price: {
      currency: "JPY",
      min: 9800,
      max: 15000,
    },
    imageUrl: "https://picsum.photos/seed/nj-tokyo/400/300",
    source: "pia.co.jp",
    sourceUrl: "https://t.pia.jp/12345",
    collectedAt: "2026-02-06T14:20:00Z",
  },
  // aespa events
  {
    id: "event-6",
    title: "aespa LIVE TOUR 'SYNK : HYPER LINE'",
    artistId: "artist-5",
    artistName: "aespa",
    category: "concert",
    date: "2026-03-28",
    time: "18:00",
    venue: "잠실 실내체육관",
    address: "서울특별시 송파구 올림픽로 25",
    city: "서울",
    country: "대한민국",
    timezone: "Asia/Seoul",
    price: {
      currency: "KRW",
      min: 132000,
      max: 176000,
    },
    imageUrl: "https://picsum.photos/seed/aespa-concert/400/300",
    ticketUrl: "https://tickets.example.com/aespa-synk",
    source: "yes24.com",
    sourceUrl: "https://ticket.yes24.com/12345",
    collectedAt: "2026-02-07T09:15:00Z",
  },
  // IU events
  {
    id: "event-7",
    title: "IU Concert 'The Golden Hour'",
    artistId: "artist-4",
    artistName: "IU",
    category: "concert",
    date: "2026-05-01",
    time: "19:00",
    venue: "잠실 올림픽 주경기장",
    address: "서울특별시 송파구 올림픽로 25",
    city: "서울",
    country: "대한민국",
    timezone: "Asia/Seoul",
    price: {
      currency: "KRW",
      min: 110000,
      max: 220000,
      tiers: [
        { name: "VIP", price: 220000 },
        { name: "R석", price: 165000 },
        { name: "S석", price: 110000 },
      ],
    },
    imageUrl: "https://picsum.photos/seed/iu-golden/400/300",
    ticketUrl: "https://tickets.example.com/iu-golden-hour",
    source: "melon.com",
    sourceUrl: "https://www.melon.com/ticket/56789",
    collectedAt: "2026-02-08T11:00:00Z",
  },
  // SEVENTEEN events
  {
    id: "event-8",
    title: "SEVENTEEN World Tour 'FOLLOW'",
    artistId: "artist-6",
    artistName: "SEVENTEEN",
    category: "concert",
    date: "2026-04-10",
    time: "18:00",
    venue: "고척스카이돔",
    address: "서울특별시 구로구 경인로 430",
    city: "서울",
    country: "대한민국",
    timezone: "Asia/Seoul",
    price: {
      currency: "KRW",
      min: 121000,
      max: 187000,
    },
    imageUrl: "https://picsum.photos/seed/svt-follow/400/300",
    source: "ticketlink.co.kr",
    sourceUrl: "https://www.ticketlink.co.kr/product/67890",
    collectedAt: "2026-02-07T16:30:00Z",
  },
  // YOASOBI events (J-POP)
  {
    id: "event-9",
    title: "YOASOBI ASIA TOUR 2026",
    artistId: "artist-9",
    artistName: "YOASOBI",
    category: "concert",
    date: "2026-06-15",
    time: "18:30",
    venue: "요코하마 아레나",
    address: "3-10 Shinyokohama, Kohoku Ward, Yokohama",
    city: "요코하마",
    country: "일본",
    timezone: "Asia/Tokyo",
    price: {
      currency: "JPY",
      min: 8800,
      max: 12000,
    },
    imageUrl: "https://picsum.photos/seed/yoasobi-asia/400/300",
    source: "pia.co.jp",
    sourceUrl: "https://t.pia.jp/67890",
    collectedAt: "2026-02-08T08:00:00Z",
  },
  // Festival event
  {
    id: "event-10",
    title: "WATERBOMB FESTIVAL 2026",
    artistId: "artist-3",
    artistName: "NewJeans",
    category: "festival",
    date: "2026-07-20",
    time: "14:00",
    venue: "잠실 종합운동장",
    address: "서울특별시 송파구 올림픽로 25",
    city: "서울",
    country: "대한민국",
    timezone: "Asia/Seoul",
    price: {
      currency: "KRW",
      min: 88000,
      max: 150000,
    },
    imageUrl: "https://picsum.photos/seed/waterbomb/400/300",
    source: "waterbombfestival.com",
    sourceUrl: "https://waterbombfestival.com/2026",
    collectedAt: "2026-02-09T12:00:00Z",
  },
];

// Mock recent searches
export const mockRecentSearches: RecentSearch[] = [
  { id: "rs-1", query: "BTS", searchedAt: "2026-02-08T14:30:00Z" },
  { id: "rs-2", query: "NewJeans 콘서트", searchedAt: "2026-02-07T10:20:00Z" },
  { id: "rs-3", query: "aespa", searchedAt: "2026-02-06T18:45:00Z" },
];

// ===== Mock Service Functions =====

function delay(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

let searchIdCounter = 1;
const searchCache: Map<string, { events: Event[]; timestamp: number }> = new Map();

export const mockSearchService = {
  // Autocomplete search (local DB simulation)
  autocompleteArtists: async (query: string): Promise<Artist[]> => {
    await delay(300);
    if (!query.trim()) return [];
    const lowerQuery = query.toLowerCase();
    return mockArtistsForSearch.filter(
      (artist) =>
        artist.name.toLowerCase().includes(lowerQuery) ||
        artist.nameKo?.toLowerCase().includes(lowerQuery)
    );
  },

  // RAG search (web crawling simulation)
  ragSearch: async (
    query: string,
    page: number = 1,
    pageSize: number = 20
  ): Promise<SearchResult> => {
    const searchStartTime = Date.now();
    const cacheKey = query.toLowerCase().trim();

    // Check cache (24 hours = 86400000 ms)
    const cached = searchCache.get(cacheKey);
    const isCached = cached && Date.now() - cached.timestamp < 86400000;

    if (!isCached) {
      // Simulate RAG search delay (3-5 seconds)
      await delay(3000 + Math.random() * 2000);
    } else {
      // Cache hit - instant response
      await delay(100);
    }

    // Filter events by query
    const lowerQuery = query.toLowerCase();
    const matchedEvents = mockEvents.filter(
      (event) =>
        event.title.toLowerCase().includes(lowerQuery) ||
        event.artistName.toLowerCase().includes(lowerQuery)
    );

    // Cache the results
    if (!isCached) {
      searchCache.set(cacheKey, { events: matchedEvents, timestamp: Date.now() });
    }

    // Pagination
    const startIndex = (page - 1) * pageSize;
    const endIndex = startIndex + pageSize;
    const paginatedEvents = matchedEvents.slice(startIndex, endIndex);

    const searchTime = (Date.now() - searchStartTime) / 1000;

    return {
      searchId: `search-${searchIdCounter++}`,
      query,
      events: paginatedEvents,
      total: matchedEvents.length,
      searchTime: Math.round(searchTime * 10) / 10,
      cached: isCached || false,
      page,
      hasMore: endIndex < matchedEvents.length,
    };
  },

  // Get search page (for infinite scroll)
  getSearchPage: async (
    searchId: string,
    page: number,
    pageSize: number = 20
  ): Promise<{ events: Event[]; hasMore: boolean }> => {
    await delay(300);
    // In real implementation, this would fetch from search cache by searchId
    // For mock, we just return empty since we don't track by searchId
    return { events: [], hasMore: false };
  },

  // Get artist by ID
  getArtist: async (artistId: string): Promise<Artist | null> => {
    await delay(300);
    return mockArtistsForSearch.find((a) => a.id === artistId) || null;
  },

  // Get artist events
  getArtistEvents: async (artistId: string): Promise<Event[]> => {
    await delay(500);
    return mockEvents.filter((e) => e.artistId === artistId);
  },

  // Get related artists (by genre/agency - simplified for MVP)
  getRelatedArtists: async (artistId: string): Promise<Artist[]> => {
    await delay(300);
    const artist = mockArtistsForSearch.find((a) => a.id === artistId);
    if (!artist) return [];

    return mockArtistsForSearch
      .filter((a) => a.id !== artistId && a.genre === artist.genre)
      .slice(0, 6);
  },

  // Get event by ID
  getEvent: async (eventId: string): Promise<Event | null> => {
    await delay(300);
    return mockEvents.find((e) => e.id === eventId) || null;
  },

  // Get recent searches
  getRecentSearches: async (): Promise<RecentSearch[]> => {
    await delay(200);
    return [...mockRecentSearches];
  },

  // Save recent search
  saveRecentSearch: async (query: string): Promise<void> => {
    await delay(100);
    const existing = mockRecentSearches.findIndex(
      (rs) => rs.query.toLowerCase() === query.toLowerCase()
    );
    if (existing >= 0) {
      mockRecentSearches.splice(existing, 1);
    }
    mockRecentSearches.unshift({
      id: `rs-${Date.now()}`,
      query,
      searchedAt: new Date().toISOString(),
    });
    // Keep only last 10
    if (mockRecentSearches.length > 10) {
      mockRecentSearches.pop();
    }
  },

  // Delete recent search
  deleteRecentSearch: async (searchId: string): Promise<void> => {
    await delay(100);
    const index = mockRecentSearches.findIndex((rs) => rs.id === searchId);
    if (index >= 0) {
      mockRecentSearches.splice(index, 1);
    }
  },

  // Clear all recent searches
  clearRecentSearches: async (): Promise<void> => {
    await delay(100);
    mockRecentSearches.length = 0;
  },

  // Get popular artists (hardcoded for MVP)
  getPopularArtists: async (): Promise<Artist[]> => {
    await delay(300);
    return mockHardcodedPopularArtists;
  },

  // Get followed artists
  getFollowedArtists: async (): Promise<Artist[]> => {
    await delay(300);
    return [...mockFollowedArtists];
  },
};

// ===== Category helpers =====

export const categoryLabels: Record<EventCategory, string> = {
  concert: "콘서트",
  fanmeeting: "팬미팅",
  broadcast: "방송",
  festival: "페스티벌",
};

export const categoryColors: Record<EventCategory, string> = {
  concert: "#007AFF", // Primary
  fanmeeting: "#5856D6", // Info
  broadcast: "#34C759", // Success
  festival: "#FF9500", // Warning
};
