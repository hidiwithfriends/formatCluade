# Artist Event Aggregator - API Specification

## 개요

FastAPI 기반 REST API. OpenAPI(Swagger) 자동 생성.

**Base URL**: `/api/v1`

---

## 인증

Bearer Token (JWT) 방식

```
Authorization: Bearer <access_token>
```

인증이 필요한 엔드포인트는 🔒 표시

---

## 엔드포인트 목록

### Auth

| Method | Endpoint | 설명 |
|--------|----------|------|
| POST | `/auth/google` | Google OAuth 로그인 |
| POST | `/auth/apple` | Apple OAuth 로그인 |
| POST | `/auth/refresh` | 토큰 갱신 |

### Users

| Method | Endpoint | 설명 |
|--------|----------|------|
| GET | `/users/me` 🔒 | 현재 사용자 정보 |
| PUT | `/users/me` 🔒 | 프로필 수정 |
| PUT | `/users/me/notifications` 🔒 | 알림 설정 수정 |
| GET | `/users/me/artists` 🔒 | 팔로우한 아티스트 목록 |
| POST | `/users/me/artists` 🔒 | 아티스트 팔로우 |
| DELETE | `/users/me/artists/{artist_id}` 🔒 | 아티스트 언팔로우 |

### Artists

| Method | Endpoint | 설명 |
|--------|----------|------|
| GET | `/artists` | 아티스트 목록 (검색 포함) |
| GET | `/artists/{artist_id}` | 아티스트 상세 |
| POST | `/artists` | 아티스트 생성 (관리자) |
| GET | `/artists/{artist_id}/events` | 아티스트 행사 목록 |
| GET | `/artists/{artist_id}/related` | 관련 아티스트 |

### Events

| Method | Endpoint | 설명 |
|--------|----------|------|
| GET | `/events` | 행사 목록 (필터 포함) |
| GET | `/events/{event_id}` | 행사 상세 |

### Search

| Method | Endpoint | 설명 |
|--------|----------|------|
| POST | `/search` | RAG 검색 |
| GET | `/search/autocomplete` | 아티스트 자동완성 |
| GET | `/search/recent` 🔒 | 최근 검색어 목록 |
| POST | `/search/recent` 🔒 | 최근 검색어 저장 |
| DELETE | `/search/recent/{search_id}` 🔒 | 최근 검색어 삭제 |
| DELETE | `/search/recent` 🔒 | 최근 검색어 전체 삭제 |

---

## 상세 스펙

### POST /search

RAG 기반 아티스트 행사 검색

**Request Body**:
```json
{
  "query": "BTS 콘서트",
  "force_refresh": false
}
```

**Query Parameters**:
- `page` (int, default=1): 페이지 번호
- `per_page` (int, default=20, max=100): 페이지 크기

**Response 200**:
```json
{
  "searchId": "uuid",
  "query": "BTS 콘서트",
  "events": [
    {
      "id": "uuid",
      "title": "BTS World Tour",
      "artistId": "uuid",
      "artistName": "BTS",
      "category": "concert",
      "date": "2026-03-15",
      "time": "18:00",
      "venue": "Seoul Olympic Stadium",
      "address": "...",
      "city": "Seoul",
      "country": "South Korea",
      "timezone": "Asia/Seoul",
      "price": {
        "currency": "KRW",
        "min": 110000,
        "max": 198000,
        "tiers": [
          {"name": "VIP", "price": 198000},
          {"name": "R석", "price": 154000}
        ]
      },
      "imageUrl": "https://...",
      "ticketUrl": "https://...",
      "source": "ticketlink.co.kr",
      "sourceUrl": "https://...",
      "collectedAt": "2026-02-05T10:30:00Z"
    }
  ],
  "total": 25,
  "searchTime": 3.5,
  "cached": false,
  "page": 1,
  "hasMore": true
}
```

---

### GET /search/autocomplete

아티스트 이름 자동완성 (로컬 DB 검색)

**Query Parameters**:
- `q` (string, required): 검색어 (1-100자)
- `limit` (int, default=10, max=20): 최대 결과 수

**Response 200**:
```json
{
  "data": [
    {
      "id": "uuid",
      "name": "BTS",
      "name_ko": "방탄소년단",
      "image_url": "https://...",
      "genre": "K-POP",
      "follower_count": 50000000
    }
  ]
}
```

---

### GET /events

행사 목록 조회 (필터 가능)

**Query Parameters**:
- `query` (string): 검색어
- `category` (enum): concert, fanmeeting, broadcast, festival
- `city` (string): 도시
- `country` (string): 국가
- `from_date` (date): 시작일 (기본: 오늘)
- `to_date` (date): 종료일
- `page` (int, default=1): 페이지 번호
- `per_page` (int, default=20): 페이지 크기

**Response 200**:
```json
{
  "data": [...],
  "total": 100,
  "page": 1,
  "per_page": 20,
  "has_more": true
}
```

---

### GET /events/{event_id}

행사 상세 조회

**Path Parameters**:
- `event_id` (UUID): 행사 ID

**Response 200**: Event 객체 (위 참조)

**Response 404**:
```json
{
  "detail": "Event not found"
}
```

---

### GET /artists/{artist_id}/events

아티스트별 행사 목록

**Path Parameters**:
- `artist_id` (UUID): 아티스트 ID

**Query Parameters**:
- `include_past` (bool, default=false): 과거 행사 포함
- `page` (int, default=1)
- `per_page` (int, default=20)

**Response 200**: EventListResponse

---

### GET /artists/{artist_id}/related

관련 아티스트 (같은 장르)

**Path Parameters**:
- `artist_id` (UUID)

**Query Parameters**:
- `limit` (int, default=6, max=20)

**Response 200**: ArtistListResponse

---

### GET /search/recent 🔒

현재 사용자의 최근 검색어

**Query Parameters**:
- `limit` (int, default=10, max=20)

**Response 200**:
```json
{
  "data": [
    {
      "id": "uuid",
      "query": "BTS",
      "searchedAt": "2026-02-08T14:30:00Z"
    }
  ]
}
```

---

### POST /search/recent 🔒

검색어 저장 (중복 시 timestamp 갱신, 최대 10개 유지)

**Request Body**:
```json
{
  "query": "BTS"
}
```

**Response 201**: RecentSearch 객체

---

### DELETE /search/recent/{search_id} 🔒

특정 검색어 삭제

**Response 200**:
```json
{
  "message": "Recent search deleted"
}
```

---

### DELETE /search/recent 🔒

모든 검색어 삭제

**Response 200**:
```json
{
  "message": "Cleared 5 recent searches"
}
```

---

## 에러 응답

### 400 Bad Request
```json
{
  "detail": "Invalid request"
}
```

### 401 Unauthorized
```json
{
  "detail": "Invalid or expired token"
}
```

### 404 Not Found
```json
{
  "detail": "Resource not found"
}
```

### 422 Validation Error
```json
{
  "detail": [
    {
      "loc": ["body", "query"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

---

## ENUM Types

### EventCategory
- `concert`: 콘서트
- `fanmeeting`: 팬미팅
- `broadcast`: 방송
- `festival`: 페스티벌

### AuthProvider
- `google`
- `apple`

---

## 캐싱 정책

### 검색 결과 캐시
- TTL: 24시간
- Key: 정규화된 검색어 (lowercase, trimmed)
- 무효화: `force_refresh=true` 사용 시

---

## 버전 히스토리

| 버전 | 날짜 | 변경 내용 |
|------|------|-----------|
| 0.1.0 | - | F1 (인증) API 구현 |
| 0.2.0 | - | F2 (검색 & RAG) API 구현 |
