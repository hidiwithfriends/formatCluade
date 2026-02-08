import { useState, useEffect } from "react";
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  Image,
  TouchableOpacity,
  ActivityIndicator,
  FlatList,
} from "react-native";
import { useLocalSearchParams, useRouter } from "expo-router";
import { SafeAreaView } from "react-native-safe-area-context";
import { EventCard } from "../../../../components/search";
import { ArtistCard } from "../../../../components/auth/ArtistCard";
import { Button } from "../../../../components/common/Button";
import { searchApi, type Event } from "../../../../lib/api/search-api";
import type { Artist } from "../../../../lib/mocks/auth";

export default function ArtistProfileScreen() {
  const router = useRouter();
  const { id } = useLocalSearchParams<{ id: string }>();

  const [artist, setArtist] = useState<Artist | null>(null);
  const [events, setEvents] = useState<Event[]>([]);
  const [relatedArtists, setRelatedArtists] = useState<Artist[]>([]);
  const [isFollowing, setIsFollowing] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [isFollowLoading, setIsFollowLoading] = useState(false);
  const [showPastEvents, setShowPastEvents] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (id) {
      loadArtistData(id);
    }
  }, [id]);

  const loadArtistData = async (artistId: string) => {
    try {
      setIsLoading(true);
      setError(null);

      const [artistData, eventsData, relatedData] = await Promise.all([
        searchApi.getArtist(artistId),
        searchApi.getArtistEvents(artistId),
        searchApi.getRelatedArtists(artistId),
      ]);

      if (!artistData) {
        setError("아티스트 정보를 찾을 수 없습니다");
        return;
      }

      setArtist(artistData);
      setEvents(eventsData);
      setRelatedArtists(relatedData);

      // Check if following (mock: check if in followed artists)
      const followed = await searchApi.getFollowedArtists();
      setIsFollowing(followed.some((a) => a.id === artistId));
    } catch (err) {
      console.error("Failed to load artist:", err);
      setError("아티스트 정보를 불러올 수 없습니다");
    } finally {
      setIsLoading(false);
    }
  };

  const handleFollowToggle = async () => {
    if (!artist || isFollowLoading) return;

    setIsFollowLoading(true);
    try {
      // Toggle follow state (in real app, call API)
      setIsFollowing(!isFollowing);
      // Show toast would be nice here
    } catch (err) {
      console.error("Follow toggle failed:", err);
    } finally {
      setIsFollowLoading(false);
    }
  };

  const handleEventPress = (event: Event) => {
    router.push(`/(tabs)/search/event/${event.id}`);
  };

  const handleRelatedArtistPress = (relatedArtist: Artist) => {
    router.push(`/(tabs)/search/artist/${relatedArtist.id}`);
  };

  const handleRetry = () => {
    if (id) {
      loadArtistData(id);
    }
  };

  // Separate upcoming and past events
  const now = new Date();
  const upcomingEvents = events.filter((e) => new Date(e.date) >= now);
  const pastEvents = events.filter((e) => new Date(e.date) < now);

  if (isLoading) {
    return (
      <SafeAreaView style={styles.container}>
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="large" color="#007AFF" />
        </View>
      </SafeAreaView>
    );
  }

  if (error || !artist) {
    return (
      <SafeAreaView style={styles.container}>
        <View style={styles.errorContainer}>
          <Text style={styles.errorIcon}>⚠️</Text>
          <Text style={styles.errorText}>{error || "오류가 발생했습니다"}</Text>
          <TouchableOpacity style={styles.retryButton} onPress={handleRetry}>
            <Text style={styles.retryButtonText}>다시 시도</Text>
          </TouchableOpacity>
        </View>
      </SafeAreaView>
    );
  }

  return (
    <ScrollView style={styles.container} showsVerticalScrollIndicator={false}>
      {/* Artist Header */}
      <View style={styles.header}>
        {/* Profile Image */}
        <View style={styles.imageContainer}>
          {artist.imageUrl ? (
            <Image source={{ uri: artist.imageUrl }} style={styles.profileImage} />
          ) : (
            <View style={[styles.profileImage, styles.imagePlaceholder]}>
              <Text style={styles.imagePlaceholderIcon}>🎤</Text>
            </View>
          )}
        </View>

        {/* Artist Info */}
        <Text style={styles.artistName}>
          {artist.name}
          {artist.nameKo && ` (${artist.nameKo})`}
        </Text>
        <Text style={styles.artistGenre}>{artist.genre}</Text>

        {/* Follow Button */}
        <View style={styles.followSection}>
          <Button
            title={isFollowing ? "팔로우 중" : "팔로우하기"}
            variant={isFollowing ? "outline" : "primary"}
            onPress={handleFollowToggle}
            loading={isFollowLoading}
            style={styles.followButton}
          />
          <Text style={styles.followerCount}>
            팔로워 {formatNumber(artist.followerCount)}명
          </Text>
        </View>
      </View>

      {/* Upcoming Events */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>
          예정된 행사 ({upcomingEvents.length})
        </Text>

        {upcomingEvents.length > 0 ? (
          upcomingEvents.map((event) => (
            <EventCard
              key={event.id}
              event={event}
              onPress={() => handleEventPress(event)}
              showSource={false}
            />
          ))
        ) : (
          <View style={styles.emptyEvents}>
            <Text style={styles.emptyIcon}>🔔</Text>
            <Text style={styles.emptyText}>예정된 행사가 없습니다</Text>
            <Text style={styles.emptyHint}>
              알림을 설정하면 새 행사를 알려드려요
            </Text>
          </View>
        )}
      </View>

      {/* Past Events Toggle */}
      {pastEvents.length > 0 && (
        <View style={styles.section}>
          <TouchableOpacity
            style={styles.pastEventsToggle}
            onPress={() => setShowPastEvents(!showPastEvents)}
          >
            <Text style={styles.pastEventsToggleText}>
              지난 행사 보기 ({pastEvents.length})
            </Text>
            <Text style={styles.toggleIcon}>{showPastEvents ? "▲" : "▼"}</Text>
          </TouchableOpacity>

          {showPastEvents &&
            pastEvents.map((event) => (
              <EventCard
                key={event.id}
                event={event}
                onPress={() => handleEventPress(event)}
                showSource={false}
              />
            ))}
        </View>
      )}

      {/* Related Artists */}
      {relatedArtists.length > 0 && (
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>관련 아티스트</Text>
          <ScrollView
            horizontal
            showsHorizontalScrollIndicator={false}
            style={styles.relatedArtistsScroll}
          >
            {relatedArtists.map((relatedArtist) => (
              <ArtistCard
                key={relatedArtist.id}
                artist={relatedArtist}
                onPress={() => handleRelatedArtistPress(relatedArtist)}
              />
            ))}
          </ScrollView>
        </View>
      )}

      {/* Bottom Padding */}
      <View style={styles.bottomPadding} />
    </ScrollView>
  );
}

// Helper function to format large numbers
function formatNumber(num: number): string {
  if (num >= 1000000) {
    return (num / 1000000).toFixed(1).replace(/\.0$/, "") + "M";
  }
  if (num >= 1000) {
    return (num / 1000).toFixed(0) + "K";
  }
  return num.toString();
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: "#FFFFFF",
  },
  loadingContainer: {
    flex: 1,
    justifyContent: "center",
    alignItems: "center",
  },
  errorContainer: {
    flex: 1,
    justifyContent: "center",
    alignItems: "center",
    padding: 40,
  },
  errorIcon: {
    fontSize: 48,
    marginBottom: 16,
  },
  errorText: {
    fontSize: 16,
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
  header: {
    alignItems: "center",
    paddingTop: 60,
    paddingHorizontal: 24,
    paddingBottom: 24,
  },
  imageContainer: {
    marginBottom: 16,
  },
  profileImage: {
    width: 120,
    height: 120,
    borderRadius: 60,
    backgroundColor: "#F5F5F5",
  },
  imagePlaceholder: {
    alignItems: "center",
    justifyContent: "center",
  },
  imagePlaceholderIcon: {
    fontSize: 48,
  },
  artistName: {
    fontSize: 24,
    fontWeight: "bold",
    color: "#000000",
    textAlign: "center",
    marginBottom: 4,
  },
  artistGenre: {
    fontSize: 16,
    color: "#666666",
    marginBottom: 16,
  },
  followSection: {
    alignItems: "center",
  },
  followButton: {
    minWidth: 160,
    marginBottom: 8,
  },
  followerCount: {
    fontSize: 14,
    color: "#666666",
  },
  section: {
    paddingHorizontal: 24,
    marginBottom: 24,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: "600",
    color: "#000000",
    marginBottom: 16,
  },
  emptyEvents: {
    alignItems: "center",
    paddingVertical: 40,
    backgroundColor: "#F5F5F5",
    borderRadius: 12,
  },
  emptyIcon: {
    fontSize: 32,
    marginBottom: 8,
  },
  emptyText: {
    fontSize: 16,
    fontWeight: "500",
    color: "#333333",
  },
  emptyHint: {
    fontSize: 14,
    color: "#666666",
    marginTop: 4,
  },
  pastEventsToggle: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    paddingVertical: 12,
    marginBottom: 16,
  },
  pastEventsToggleText: {
    fontSize: 16,
    color: "#007AFF",
    fontWeight: "500",
  },
  toggleIcon: {
    fontSize: 12,
    color: "#007AFF",
  },
  relatedArtistsScroll: {
    marginLeft: -8,
  },
  bottomPadding: {
    height: 40,
  },
});
