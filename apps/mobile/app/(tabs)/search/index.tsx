import { useState, useEffect, useCallback } from "react";
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  FlatList,
  ActivityIndicator,
  RefreshControl,
} from "react-native";
import { useLocalSearchParams, useRouter } from "expo-router";
import { SafeAreaView } from "react-native-safe-area-context";
import { ArtistSearchInput } from "../../../components/common/ArtistSearchInput";
import { EventCard, CategoryBadge } from "../../../components/search";
import { ArtistCard } from "../../../components/auth/ArtistCard";
import {
  searchApi,
  type Event,
  type SearchResult,
  type RecentSearch,
  categoryLabels,
} from "../../../lib/api/search-api";
import type { Artist } from "../../../lib/mocks/auth";
import type { EventCategory } from "../../../lib/mocks/search-rag";

type SearchState = "home" | "searching" | "results" | "error";
type CategoryFilter = "all" | EventCategory;

export default function SearchScreen() {
  const router = useRouter();
  const params = useLocalSearchParams<{ q?: string }>();

  // State
  const [searchState, setSearchState] = useState<SearchState>("home");
  const [searchResult, setSearchResult] = useState<SearchResult | null>(null);
  const [recentSearches, setRecentSearches] = useState<RecentSearch[]>([]);
  const [popularArtists, setPopularArtists] = useState<Artist[]>([]);
  const [followedArtists, setFollowedArtists] = useState<Artist[]>([]);
  const [categoryFilter, setCategoryFilter] = useState<CategoryFilter>("all");
  const [isLoading, setIsLoading] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");

  // Load initial data
  useEffect(() => {
    loadHomeData();
  }, []);

  // Handle URL query parameter
  useEffect(() => {
    if (params.q) {
      performSearch(params.q);
    }
  }, [params.q]);

  const loadHomeData = async () => {
    try {
      setIsLoading(true);
      const [recent, popular, followed] = await Promise.all([
        searchApi.getRecentSearches(),
        searchApi.getPopularArtists(),
        searchApi.getFollowedArtists(),
      ]);
      setRecentSearches(recent);
      setPopularArtists(popular);
      setFollowedArtists(followed);
    } catch (error) {
      console.error("Failed to load home data:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const performSearch = async (query: string) => {
    try {
      setSearchState("searching");
      setErrorMessage("");
      setCategoryFilter("all");

      const result = await searchApi.ragSearch(query);
      setSearchResult(result);
      setSearchState("results");

      // Save to recent searches
      await searchApi.saveRecentSearch(query);
      const updated = await searchApi.getRecentSearches();
      setRecentSearches(updated);
    } catch (error) {
      console.error("Search error:", error);
      setErrorMessage("검색에 실패했습니다. 다시 시도해주세요.");
      setSearchState("error");
    }
  };

  const handleArtistSelect = (artist: Artist) => {
    router.push(`/(tabs)/search/artist/${artist.id}`);
  };

  const handleWebSearch = (query: string) => {
    router.setParams({ q: query });
  };

  const handleEventPress = (event: Event) => {
    router.push(`/(tabs)/search/event/${event.id}`);
  };

  const handleRecentSearchPress = (query: string) => {
    router.setParams({ q: query });
  };

  const handleClearRecentSearches = async () => {
    await searchApi.clearRecentSearches();
    setRecentSearches([]);
  };

  const handleBackToHome = () => {
    setSearchState("home");
    setSearchResult(null);
    router.setParams({ q: undefined });
  };

  const handleRefresh = async () => {
    setIsRefreshing(true);
    await loadHomeData();
    setIsRefreshing(false);
  };

  const handleRetry = () => {
    if (params.q) {
      performSearch(params.q);
    }
  };

  // Filter events by category
  const filteredEvents = searchResult?.events.filter((event) =>
    categoryFilter === "all" ? true : event.category === categoryFilter
  );

  // Render based on state
  const renderContent = () => {
    if (isLoading && searchState === "home") {
      return (
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="large" color="#007AFF" />
        </View>
      );
    }

    if (searchState === "searching") {
      return (
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="large" color="#007AFF" />
          <Text style={styles.loadingText}>행사 정보를 검색하고 있습니다...</Text>
          <Text style={styles.loadingSubtext}>웹에서 최신 정보를 수집 중</Text>
        </View>
      );
    }

    if (searchState === "error") {
      return (
        <View style={styles.emptyContainer}>
          <Text style={styles.emptyIcon}>⚠️</Text>
          <Text style={styles.emptyTitle}>{errorMessage}</Text>
          <TouchableOpacity style={styles.retryButton} onPress={handleRetry}>
            <Text style={styles.retryButtonText}>다시 시도</Text>
          </TouchableOpacity>
        </View>
      );
    }

    if (searchState === "results" && searchResult) {
      return renderSearchResults();
    }

    return renderHomeContent();
  };

  const renderHomeContent = () => (
    <ScrollView
      style={styles.scrollView}
      showsVerticalScrollIndicator={false}
      refreshControl={
        <RefreshControl refreshing={isRefreshing} onRefresh={handleRefresh} />
      }
    >
      {/* Recent Searches */}
      {recentSearches.length > 0 && (
        <View style={styles.section}>
          <View style={styles.sectionHeader}>
            <Text style={styles.sectionTitle}>최근 검색</Text>
            <TouchableOpacity onPress={handleClearRecentSearches}>
              <Text style={styles.clearButton}>전체삭제</Text>
            </TouchableOpacity>
          </View>
          <ScrollView
            horizontal
            showsHorizontalScrollIndicator={false}
            style={styles.chipsContainer}
          >
            {recentSearches.map((item) => (
              <TouchableOpacity
                key={item.id}
                style={styles.chip}
                onPress={() => handleRecentSearchPress(item.query)}
              >
                <Text style={styles.chipText}>{item.query}</Text>
              </TouchableOpacity>
            ))}
          </ScrollView>
        </View>
      )}

      {/* My Artists */}
      {followedArtists.length > 0 && (
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>내 아티스트</Text>
          <ScrollView
            horizontal
            showsHorizontalScrollIndicator={false}
            style={styles.artistsRow}
          >
            {followedArtists.map((artist) => (
              <ArtistCard
                key={artist.id}
                artist={artist}
                onPress={() => handleArtistSelect(artist)}
              />
            ))}
          </ScrollView>
        </View>
      )}

      {/* Popular Artists */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>인기 아티스트</Text>
        <View style={styles.artistsGrid}>
          {popularArtists.map((artist) => (
            <ArtistCard
              key={artist.id}
              artist={artist}
              onPress={() => handleArtistSelect(artist)}
            />
          ))}
        </View>
      </View>
    </ScrollView>
  );

  const renderSearchResults = () => {
    if (!searchResult) return null;

    const categories: { key: CategoryFilter; label: string }[] = [
      { key: "all", label: "전체" },
      { key: "concert", label: categoryLabels.concert },
      { key: "fanmeeting", label: categoryLabels.fanmeeting },
      { key: "broadcast", label: categoryLabels.broadcast },
      { key: "festival", label: categoryLabels.festival },
    ];

    return (
      <View style={styles.resultsContainer}>
        {/* Results Summary */}
        <View style={styles.resultsSummary}>
          <Text style={styles.summaryText}>
            {searchResult.total}건 · {searchResult.searchTime}초
          </Text>
          {searchResult.cached && (
            <View style={styles.cachedBadge}>
              <Text style={styles.cachedText}>캐시됨</Text>
            </View>
          )}
        </View>

        {/* Category Filter */}
        <ScrollView
          horizontal
          showsHorizontalScrollIndicator={false}
          style={styles.categoryFilter}
        >
          {categories.map((cat) => (
            <TouchableOpacity
              key={cat.key}
              style={[
                styles.categoryTab,
                categoryFilter === cat.key && styles.categoryTabActive,
              ]}
              onPress={() => setCategoryFilter(cat.key)}
            >
              <Text
                style={[
                  styles.categoryTabText,
                  categoryFilter === cat.key && styles.categoryTabTextActive,
                ]}
              >
                {cat.label}
              </Text>
            </TouchableOpacity>
          ))}
        </ScrollView>

        {/* Results List */}
        {filteredEvents && filteredEvents.length > 0 ? (
          <FlatList
            data={filteredEvents}
            keyExtractor={(item) => item.id}
            renderItem={({ item }) => (
              <EventCard event={item} onPress={() => handleEventPress(item)} />
            )}
            contentContainerStyle={styles.resultsList}
            showsVerticalScrollIndicator={false}
          />
        ) : (
          <View style={styles.emptyContainer}>
            <Text style={styles.emptyIcon}>🔍</Text>
            <Text style={styles.emptyTitle}>행사 정보를 찾을 수 없습니다</Text>
            <Text style={styles.emptySubtitle}>
              다른 검색어를 시도해보세요
            </Text>
          </View>
        )}
      </View>
    );
  };

  return (
    <SafeAreaView style={styles.container} edges={["top"]}>
      {/* Header */}
      <View style={styles.header}>
        {searchState === "results" ? (
          <TouchableOpacity onPress={handleBackToHome} style={styles.backButton}>
            <Text style={styles.backIcon}>←</Text>
          </TouchableOpacity>
        ) : null}
        <Text style={styles.headerTitle}>검색</Text>
      </View>

      {/* Search Input */}
      <View style={styles.searchContainer}>
        <ArtistSearchInput
          placeholder="아티스트 또는 행사 검색"
          onArtistSelect={handleArtistSelect}
          onWebSearch={handleWebSearch}
          showWebSearchOption={true}
        />
      </View>

      {/* Content */}
      {renderContent()}
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: "#FFFFFF",
  },
  header: {
    flexDirection: "row",
    alignItems: "center",
    paddingHorizontal: 24,
    paddingVertical: 12,
  },
  backButton: {
    marginRight: 12,
    padding: 4,
  },
  backIcon: {
    fontSize: 24,
    color: "#000000",
  },
  headerTitle: {
    fontSize: 32,
    fontWeight: "bold",
    color: "#000000",
  },
  searchContainer: {
    paddingHorizontal: 24,
    marginBottom: 16,
    zIndex: 100,
  },
  scrollView: {
    flex: 1,
  },
  section: {
    marginBottom: 24,
    paddingHorizontal: 24,
  },
  sectionHeader: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: 12,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: "600",
    color: "#000000",
    marginBottom: 12,
  },
  clearButton: {
    fontSize: 14,
    color: "#007AFF",
  },
  chipsContainer: {
    marginTop: -4,
  },
  chip: {
    backgroundColor: "#F5F5F5",
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 20,
    marginRight: 8,
  },
  chipText: {
    fontSize: 14,
    color: "#333333",
  },
  artistsRow: {
    marginTop: -4,
  },
  artistsGrid: {
    flexDirection: "row",
    flexWrap: "wrap",
    marginTop: -4,
  },
  loadingContainer: {
    flex: 1,
    justifyContent: "center",
    alignItems: "center",
    padding: 40,
  },
  loadingText: {
    marginTop: 16,
    fontSize: 16,
    fontWeight: "500",
    color: "#333333",
  },
  loadingSubtext: {
    marginTop: 4,
    fontSize: 14,
    color: "#666666",
  },
  emptyContainer: {
    flex: 1,
    justifyContent: "center",
    alignItems: "center",
    padding: 40,
  },
  emptyIcon: {
    fontSize: 48,
    marginBottom: 16,
  },
  emptyTitle: {
    fontSize: 18,
    fontWeight: "600",
    color: "#000000",
    marginBottom: 8,
    textAlign: "center",
  },
  emptySubtitle: {
    fontSize: 14,
    color: "#666666",
    textAlign: "center",
  },
  retryButton: {
    marginTop: 20,
    backgroundColor: "#007AFF",
    paddingHorizontal: 24,
    paddingVertical: 12,
    borderRadius: 12,
  },
  retryButtonText: {
    color: "#FFFFFF",
    fontSize: 16,
    fontWeight: "600",
  },
  resultsContainer: {
    flex: 1,
  },
  resultsSummary: {
    flexDirection: "row",
    alignItems: "center",
    paddingHorizontal: 24,
    marginBottom: 12,
  },
  summaryText: {
    fontSize: 14,
    color: "#666666",
  },
  cachedBadge: {
    backgroundColor: "#E8F4FF",
    paddingHorizontal: 8,
    paddingVertical: 2,
    borderRadius: 4,
    marginLeft: 8,
  },
  cachedText: {
    fontSize: 12,
    color: "#007AFF",
    fontWeight: "500",
  },
  categoryFilter: {
    paddingHorizontal: 24,
    marginBottom: 16,
  },
  categoryTab: {
    paddingHorizontal: 16,
    paddingVertical: 8,
    marginRight: 8,
    borderRadius: 20,
    backgroundColor: "#F5F5F5",
  },
  categoryTabActive: {
    backgroundColor: "#007AFF",
  },
  categoryTabText: {
    fontSize: 14,
    color: "#666666",
    fontWeight: "500",
  },
  categoryTabTextActive: {
    color: "#FFFFFF",
  },
  resultsList: {
    paddingHorizontal: 24,
    paddingBottom: 24,
  },
});
