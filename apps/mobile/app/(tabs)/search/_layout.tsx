import { Stack } from "expo-router";

export default function SearchLayout() {
  return (
    <Stack
      screenOptions={{
        headerShown: false,
      }}
    >
      <Stack.Screen name="index" />
      <Stack.Screen
        name="artist/[id]"
        options={{
          headerShown: true,
          headerBackTitle: "검색",
          headerTitle: "",
          headerTransparent: true,
        }}
      />
      <Stack.Screen
        name="event/[id]"
        options={{
          headerShown: true,
          headerBackTitle: "뒤로",
          headerTitle: "",
          headerTransparent: true,
        }}
      />
    </Stack>
  );
}
