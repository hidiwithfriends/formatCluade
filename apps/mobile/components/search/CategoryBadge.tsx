import { View, Text, StyleSheet } from "react-native";
import {
  type EventCategory,
  categoryLabels,
  categoryColors,
} from "../../lib/api/search-api";

interface CategoryBadgeProps {
  category: EventCategory;
  size?: "small" | "medium";
}

export function CategoryBadge({ category, size = "medium" }: CategoryBadgeProps) {
  const backgroundColor = categoryColors[category];
  const label = categoryLabels[category];

  return (
    <View
      style={[
        styles.badge,
        size === "small" && styles.badgeSmall,
        { backgroundColor },
      ]}
    >
      <Text style={[styles.text, size === "small" && styles.textSmall]}>
        {label}
      </Text>
    </View>
  );
}

const styles = StyleSheet.create({
  badge: {
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: 6,
    alignSelf: "flex-start",
  },
  badgeSmall: {
    paddingHorizontal: 8,
    paddingVertical: 2,
  },
  text: {
    color: "#FFFFFF",
    fontSize: 12,
    fontWeight: "600",
  },
  textSmall: {
    fontSize: 10,
  },
});
