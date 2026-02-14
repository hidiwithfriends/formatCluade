export { apiClient } from "./client";
export {
  authApi,
  userApi,
  artistApi,
  setAccessToken,
  getAccessToken,
  type User,
  type Artist,
  type TokenResponse,
  type ArtistListResponse,
  type FollowArtistResponse,
  type MessageResponse,
  type UserUpdate,
  type NotificationUpdate,
  type AuthProvider,
} from "./auth-api";
export {
  searchApi,
  categoryLabels,
  categoryColors,
  type Event,
  type SearchResult,
  type RecentSearch,
} from "./search-api";
