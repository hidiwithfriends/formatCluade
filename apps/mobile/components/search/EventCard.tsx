import { TouchableOpacity, View, Text, Image, StyleSheet } from "react-native";
import { CategoryBadge } from "./CategoryBadge";
import type { Event } from "../../lib/api/search-api";

interface EventCardProps {
  event: Event;
  onPress: () => void;
  showSource?: boolean;
}

export function EventCard({ event, onPress, showSource = true }: EventCardProps) {
  // Format date
  const formatDate = (dateStr: string): string => {
    const date = new Date(dateStr);
    const options: Intl.DateTimeFormatOptions = {
      year: "numeric",
      month: "2-digit",
      day: "2-digit",
      weekday: "short",
    };
    return date.toLocaleDateString("ko-KR", options);
  };

  return (
    <TouchableOpacity style={styles.container} onPress={onPress} activeOpacity={0.7}>
      {event.imageUrl && (
        <Image source={{ uri: event.imageUrl }} style={styles.image} />
      )}
      <View style={styles.content}>
        <Text style={styles.title} numberOfLines={2}>
          {event.title}
        </Text>
        <View style={styles.row}>
          <Text style={styles.icon}>📅</Text>
          <Text style={styles.info}>{formatDate(event.date)}</Text>
        </View>
        <View style={styles.row}>
          <Text style={styles.icon}>📍</Text>
          <Text style={styles.info} numberOfLines={1}>
            {event.venue}
          </Text>
        </View>
        <View style={styles.footer}>
          <CategoryBadge category={event.category} size="small" />
          {showSource && (
            <Text style={styles.source}>출처: {event.source}</Text>
          )}
        </View>
      </View>
    </TouchableOpacity>
  );
}

const styles = StyleSheet.create({
  container: {
    backgroundColor: "#FFFFFF",
    borderRadius: 12,
    marginBottom: 12,
    shadowColor: "#000000",
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.08,
    shadowRadius: 8,
    elevation: 2,
    overflow: "hidden",
  },
  image: {
    width: "100%",
    height: 160,
    backgroundColor: "#F5F5F5",
  },
  content: {
    padding: 16,
  },
  title: {
    fontSize: 16,
    fontWeight: "600",
    color: "#000000",
    marginBottom: 8,
    lineHeight: 22,
  },
  row: {
    flexDirection: "row",
    alignItems: "center",
    marginBottom: 4,
  },
  icon: {
    fontSize: 14,
    marginRight: 6,
  },
  info: {
    fontSize: 14,
    color: "#666666",
    flex: 1,
  },
  footer: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
    marginTop: 8,
  },
  source: {
    fontSize: 12,
    color: "#999999",
  },
});
