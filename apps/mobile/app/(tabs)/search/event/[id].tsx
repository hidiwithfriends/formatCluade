import { useState, useEffect } from "react";
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  Image,
  TouchableOpacity,
  ActivityIndicator,
  Alert,
} from "react-native";
import { useLocalSearchParams, useRouter } from "expo-router";
import { SafeAreaView } from "react-native-safe-area-context";
import { CategoryBadge } from "../../../../components/search";
import { Button } from "../../../../components/common/Button";
import { searchApi, type Event } from "../../../../lib/api/search-api";

export default function EventDetailScreen() {
  const router = useRouter();
  const { id } = useLocalSearchParams<{ id: string }>();

  const [event, setEvent] = useState<Event | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (id) {
      loadEventData(id);
    }
  }, [id]);

  const loadEventData = async (eventId: string) => {
    try {
      setIsLoading(true);
      setError(null);

      const eventData = await searchApi.getEvent(eventId);

      if (!eventData) {
        setError("행사 정보를 찾을 수 없습니다");
        return;
      }

      setEvent(eventData);
    } catch (err) {
      console.error("Failed to load event:", err);
      setError("행사 정보를 불러올 수 없습니다");
    } finally {
      setIsLoading(false);
    }
  };

  const handleArtistPress = () => {
    if (event) {
      router.push(`/(tabs)/search/artist/${event.artistId}`);
    }
  };

  const handleTicketPress = () => {
    // F5에서 완성 예정 - 현재는 토스트 표시
    Alert.alert("곧 지원 예정입니다", "티켓 예매 기능은 곧 추가될 예정입니다.");
  };

  const handleCalendarPress = () => {
    // F3에서 완성 예정 - 현재는 토스트 표시
    Alert.alert("곧 지원 예정입니다", "캘린더 추가 기능은 곧 추가될 예정입니다.");
  };

  const handleNotificationPress = () => {
    // F4에서 완성 예정 - 현재는 토스트 표시
    Alert.alert("곧 지원 예정입니다", "알림 설정 기능은 곧 추가될 예정입니다.");
  };

  const handleRetry = () => {
    if (id) {
      loadEventData(id);
    }
  };

  // Format date for display
  const formatDate = (dateStr: string): string => {
    const date = new Date(dateStr);
    const options: Intl.DateTimeFormatOptions = {
      year: "numeric",
      month: "long",
      day: "numeric",
      weekday: "long",
    };
    return date.toLocaleDateString("ko-KR", options);
  };

  // Format time for display
  const formatTime = (time: string, timezone: string): string => {
    // Extract timezone abbreviation from IANA timezone
    const tzAbbr = getTimezoneAbbr(timezone);
    return `${time} (${tzAbbr})`;
  };

  // Get timezone abbreviation
  const getTimezoneAbbr = (timezone: string): string => {
    const tzMap: Record<string, string> = {
      "Asia/Seoul": "KST",
      "Asia/Tokyo": "JST",
      "America/Los_Angeles": "PST",
      "America/New_York": "EST",
    };
    return tzMap[timezone] || timezone;
  };

  // Format price for display
  const formatPrice = (price: number, currency: string): string => {
    if (currency === "KRW") {
      return `₩${price.toLocaleString()}`;
    } else if (currency === "JPY") {
      return `¥${price.toLocaleString()}`;
    } else if (currency === "USD") {
      return `$${price.toLocaleString()}`;
    }
    return `${currency} ${price.toLocaleString()}`;
  };

  // Format collected date
  const formatCollectedDate = (dateStr: string): string => {
    const date = new Date(dateStr);
    return date.toLocaleDateString("ko-KR", {
      year: "numeric",
      month: "2-digit",
      day: "2-digit",
    });
  };

  if (isLoading) {
    return (
      <SafeAreaView style={styles.container}>
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="large" color="#007AFF" />
        </View>
      </SafeAreaView>
    );
  }

  if (error || !event) {
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
      {/* Event Image */}
      {event.imageUrl && (
        <Image source={{ uri: event.imageUrl }} style={styles.heroImage} />
      )}

      <View style={styles.content}>
        {/* Title & Category */}
        <Text style={styles.title}>{event.title}</Text>
        <CategoryBadge category={event.category} />

        {/* Artist Link */}
        <TouchableOpacity style={styles.artistLink} onPress={handleArtistPress}>
          <Text style={styles.artistIcon}>🎤</Text>
          <Text style={styles.artistName}>{event.artistName}</Text>
          <Text style={styles.artistArrow}>▶</Text>
        </TouchableOpacity>

        <View style={styles.divider} />

        {/* Date & Time */}
        <View style={styles.infoSection}>
          <Text style={styles.infoIcon}>📅</Text>
          <View style={styles.infoContent}>
            <Text style={styles.infoLabel}>날짜</Text>
            <Text style={styles.infoValue}>{formatDate(event.date)}</Text>
            <Text style={styles.infoValue}>
              {formatTime(event.time, event.timezone)}
            </Text>
          </View>
        </View>

        {/* Venue */}
        <View style={styles.infoSection}>
          <Text style={styles.infoIcon}>📍</Text>
          <View style={styles.infoContent}>
            <Text style={styles.infoLabel}>장소</Text>
            <Text style={styles.infoValue}>{event.venue}</Text>
            <Text style={styles.infoSubvalue}>{event.address}</Text>
          </View>
        </View>

        {/* Price */}
        {event.price && (
          <View style={styles.infoSection}>
            <Text style={styles.infoIcon}>💰</Text>
            <View style={styles.infoContent}>
              <Text style={styles.infoLabel}>가격</Text>
              {event.price.tiers ? (
                event.price.tiers.map((tier, index) => (
                  <Text key={index} style={styles.infoValue}>
                    {tier.name}: {formatPrice(tier.price, event.price!.currency)}
                  </Text>
                ))
              ) : (
                <Text style={styles.infoValue}>
                  {formatPrice(event.price.min, event.price.currency)}
                  {event.price.min !== event.price.max &&
                    ` ~ ${formatPrice(event.price.max, event.price.currency)}`}
                </Text>
              )}
            </View>
          </View>
        )}

        <View style={styles.divider} />

        {/* Action Buttons */}
        <View style={styles.actionSection}>
          {/* Ticket Button - Disabled */}
          <Button
            title="🎫 티켓 예매하기"
            variant="primary"
            onPress={handleTicketPress}
            disabled={true}
            style={styles.ticketButton}
          />

          {/* Calendar & Notification Buttons - Disabled */}
          <View style={styles.buttonRow}>
            <Button
              title="📅 캘린더 추가"
              variant="outline"
              onPress={handleCalendarPress}
              disabled={true}
              style={styles.halfButton}
            />
            <Button
              title="🔔 알림 설정"
              variant="outline"
              onPress={handleNotificationPress}
              disabled={true}
              style={styles.halfButton}
            />
          </View>
        </View>

        <View style={styles.divider} />

        {/* Source Info */}
        <View style={styles.sourceSection}>
          <Text style={styles.sourceLabel}>ℹ️ 정보 출처</Text>
          <Text style={styles.sourceValue}>{event.source}</Text>
          <Text style={styles.sourceDate}>
            수집일: {formatCollectedDate(event.collectedAt)}
          </Text>
        </View>
      </View>

      {/* Bottom Padding */}
      <View style={styles.bottomPadding} />
    </ScrollView>
  );
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
  heroImage: {
    width: "100%",
    height: 250,
    backgroundColor: "#F5F5F5",
  },
  content: {
    padding: 24,
  },
  title: {
    fontSize: 24,
    fontWeight: "bold",
    color: "#000000",
    marginBottom: 12,
    lineHeight: 32,
  },
  artistLink: {
    flexDirection: "row",
    alignItems: "center",
    paddingVertical: 16,
    marginTop: 16,
  },
  artistIcon: {
    fontSize: 20,
    marginRight: 8,
  },
  artistName: {
    fontSize: 16,
    fontWeight: "600",
    color: "#000000",
    flex: 1,
  },
  artistArrow: {
    fontSize: 12,
    color: "#999999",
  },
  divider: {
    height: 1,
    backgroundColor: "#E5E5E5",
    marginVertical: 16,
  },
  infoSection: {
    flexDirection: "row",
    paddingVertical: 12,
  },
  infoIcon: {
    fontSize: 20,
    marginRight: 12,
    width: 28,
  },
  infoContent: {
    flex: 1,
  },
  infoLabel: {
    fontSize: 14,
    color: "#666666",
    marginBottom: 4,
  },
  infoValue: {
    fontSize: 16,
    color: "#000000",
    marginBottom: 2,
  },
  infoSubvalue: {
    fontSize: 14,
    color: "#666666",
    marginTop: 2,
  },
  actionSection: {
    marginVertical: 8,
  },
  ticketButton: {
    marginBottom: 12,
  },
  buttonRow: {
    flexDirection: "row",
    gap: 12,
  },
  halfButton: {
    flex: 1,
  },
  sourceSection: {
    paddingVertical: 8,
  },
  sourceLabel: {
    fontSize: 14,
    color: "#666666",
    marginBottom: 4,
  },
  sourceValue: {
    fontSize: 14,
    color: "#999999",
  },
  sourceDate: {
    fontSize: 12,
    color: "#999999",
    marginTop: 2,
  },
  bottomPadding: {
    height: 40,
  },
});
