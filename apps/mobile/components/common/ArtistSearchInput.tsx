import { useState, useCallback } from "react";
import {
  View,
  TextInput,
  Text,
  TouchableOpacity,
  FlatList,
  Image,
  StyleSheet,
  ActivityIndicator,
} from "react-native";
import { searchApi } from "../../lib/api/search-api";
import type { Artist } from "../../lib/mocks/auth";

interface ArtistSearchInputProps {
  placeholder?: string;
  onArtistSelect: (artist: Artist) => void;
  onWebSearch?: (query: string) => void;
  showWebSearchOption?: boolean;
  autoFocus?: boolean;
}

export function ArtistSearchInput({
  placeholder = "아티스트 검색...",
  onArtistSelect,
  onWebSearch,
  showWebSearchOption = true,
  autoFocus = false,
}: ArtistSearchInputProps) {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<Artist[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isFocused, setIsFocused] = useState(false);

  const handleSearch = useCallback(async (text: string) => {
    setQuery(text);
    if (text.trim().length === 0) {
      setResults([]);
      return;
    }

    setIsLoading(true);
    try {
      const artists = await searchApi.autocompleteArtists(text);
      setResults(artists);
    } catch (error) {
      console.error("Search error:", error);
      setResults([]);
    } finally {
      setIsLoading(false);
    }
  }, []);

  const handleArtistPress = (artist: Artist) => {
    setQuery("");
    setResults([]);
    setIsFocused(false);
    onArtistSelect(artist);
  };

  const handleWebSearchPress = () => {
    if (onWebSearch && query.trim()) {
      onWebSearch(query.trim());
      setQuery("");
      setResults([]);
      setIsFocused(false);
    }
  };

  const handleClear = () => {
    setQuery("");
    setResults([]);
  };

  const showDropdown = isFocused && query.trim().length > 0;

  return (
    <View style={styles.container}>
      <View style={styles.inputContainer}>
        <Text style={styles.searchIcon}>🔍</Text>
        <TextInput
          style={styles.input}
          placeholder={placeholder}
          placeholderTextColor="#999999"
          value={query}
          onChangeText={handleSearch}
          onFocus={() => setIsFocused(true)}
          onBlur={() => setTimeout(() => setIsFocused(false), 200)}
          autoFocus={autoFocus}
          returnKeyType="search"
          onSubmitEditing={handleWebSearchPress}
        />
        {query.length > 0 && (
          <TouchableOpacity onPress={handleClear} style={styles.clearButton}>
            <Text style={styles.clearIcon}>×</Text>
          </TouchableOpacity>
        )}
        {isLoading && (
          <ActivityIndicator size="small" color="#007AFF" style={styles.loader} />
        )}
      </View>

      {showDropdown && (
        <View style={styles.dropdown}>
          {/* Web Search Option */}
          {showWebSearchOption && (
            <TouchableOpacity
              style={styles.webSearchOption}
              onPress={handleWebSearchPress}
            >
              <Text style={styles.webSearchIcon}>🌐</Text>
              <View style={styles.webSearchContent}>
                <Text style={styles.webSearchTitle}>
                  "{query}" 웹에서 검색
                </Text>
                <Text style={styles.webSearchSubtitle}>
                  최신 행사 정보를 찾습니다
                </Text>
              </View>
            </TouchableOpacity>
          )}

          {/* Autocomplete Results */}
          {results.length > 0 ? (
            <FlatList
              data={results}
              keyExtractor={(item) => item.id}
              renderItem={({ item }) => (
                <TouchableOpacity
                  style={styles.resultItem}
                  onPress={() => handleArtistPress(item)}
                >
                  {item.imageUrl ? (
                    <Image source={{ uri: item.imageUrl }} style={styles.artistImage} />
                  ) : (
                    <View style={[styles.artistImage, styles.artistPlaceholder]}>
                      <Text style={styles.artistPlaceholderIcon}>🎤</Text>
                    </View>
                  )}
                  <View style={styles.artistInfo}>
                    <Text style={styles.artistName}>
                      {item.name}
                      {item.nameKo && ` (${item.nameKo})`}
                    </Text>
                    <Text style={styles.artistGenre}>{item.genre}</Text>
                  </View>
                </TouchableOpacity>
              )}
              style={styles.resultsList}
              keyboardShouldPersistTaps="handled"
            />
          ) : (
            !isLoading &&
            query.trim().length > 0 && (
              <View style={styles.noResults}>
                <Text style={styles.noResultsText}>
                  일치하는 아티스트가 없습니다
                </Text>
                <Text style={styles.noResultsHint}>
                  웹에서 검색을 시도해보세요
                </Text>
              </View>
            )
          )}
        </View>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    position: "relative",
    zIndex: 100,
  },
  inputContainer: {
    flexDirection: "row",
    alignItems: "center",
    backgroundColor: "#F5F5F5",
    borderRadius: 12,
    paddingHorizontal: 16,
    height: 48,
  },
  searchIcon: {
    fontSize: 16,
    marginRight: 8,
  },
  input: {
    flex: 1,
    fontSize: 16,
    color: "#000000",
    height: "100%",
  },
  clearButton: {
    padding: 4,
  },
  clearIcon: {
    fontSize: 20,
    color: "#999999",
  },
  loader: {
    marginLeft: 8,
  },
  dropdown: {
    position: "absolute",
    top: 52,
    left: 0,
    right: 0,
    backgroundColor: "#FFFFFF",
    borderRadius: 12,
    shadowColor: "#000000",
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.15,
    shadowRadius: 12,
    elevation: 8,
    maxHeight: 350,
    overflow: "hidden",
  },
  webSearchOption: {
    flexDirection: "row",
    alignItems: "center",
    padding: 16,
    borderBottomWidth: 1,
    borderBottomColor: "#E5E5E5",
    backgroundColor: "#F8F9FA",
  },
  webSearchIcon: {
    fontSize: 20,
    marginRight: 12,
  },
  webSearchContent: {
    flex: 1,
  },
  webSearchTitle: {
    fontSize: 15,
    fontWeight: "600",
    color: "#007AFF",
  },
  webSearchSubtitle: {
    fontSize: 12,
    color: "#666666",
    marginTop: 2,
  },
  resultsList: {
    maxHeight: 250,
  },
  resultItem: {
    flexDirection: "row",
    alignItems: "center",
    padding: 12,
    borderBottomWidth: 1,
    borderBottomColor: "#F5F5F5",
  },
  artistImage: {
    width: 44,
    height: 44,
    borderRadius: 22,
    backgroundColor: "#F5F5F5",
    marginRight: 12,
  },
  artistPlaceholder: {
    alignItems: "center",
    justifyContent: "center",
  },
  artistPlaceholderIcon: {
    fontSize: 20,
  },
  artistInfo: {
    flex: 1,
  },
  artistName: {
    fontSize: 15,
    fontWeight: "500",
    color: "#000000",
  },
  artistGenre: {
    fontSize: 13,
    color: "#666666",
    marginTop: 2,
  },
  noResults: {
    padding: 20,
    alignItems: "center",
  },
  noResultsText: {
    fontSize: 14,
    color: "#666666",
  },
  noResultsHint: {
    fontSize: 12,
    color: "#999999",
    marginTop: 4,
  },
});
