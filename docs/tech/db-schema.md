# Artist Event Aggregator - Database Schema

## 개요

PostgreSQL + pgvector를 사용하며, SQLAlchemy ORM으로 관리합니다.

## ERD (Entity Relationship Diagram)

```
┌─────────────────────┐         ┌─────────────────────┐
│       users         │         │      artists        │
├─────────────────────┤         ├─────────────────────┤
│ id (PK, UUID)       │         │ id (PK, UUID)       │
│ email (UNIQUE)      │         │ name                │
│ name                │         │ name_ko             │
│ profile_image       │    ┌───>│ image_url           │
│ provider            │    │    │ genre               │
│ provider_id         │    │    │ follower_count      │
│ notification_enabled│    │    │ created_at          │
│ notification_*      │    │    │ updated_at          │
│ created_at          │    │    └──────────┬──────────┘
│ updated_at          │    │               │
└──────────┬──────────┘    │               │
           │               │               │
           │    ┌──────────┴──────────┐    │
           │    │    user_artists     │    │
           │    ├─────────────────────┤    │
           └───>│ id (PK, UUID)       │    │
                │ user_id (FK)        │    │
                │ artist_id (FK)      │    │
                │ created_at          │    │
                └─────────────────────┘    │
                                           │
           ┌───────────────────────────────┘
           │
           ▼
┌─────────────────────┐         ┌─────────────────────┐
│       events        │         │  event_embeddings   │
├─────────────────────┤         ├─────────────────────┤
│ id (PK, UUID)       │<───────>│ id (PK, UUID)       │
│ title               │  1:1    │ event_id (FK, UQ)   │
│ category            │         │ embedding (vector)  │
│ artist_id (FK)      │         │ embedded_text       │
│ artist_name         │         │ model               │
│ event_date          │         │ created_at          │
│ event_time          │         └─────────────────────┘
│ timezone            │
│ venue               │
│ address             │
│ city                │
│ country             │
│ price_*             │
│ image_url           │
│ ticket_url          │
│ source              │
│ source_url          │
│ collected_at        │
│ created_at          │
│ updated_at          │
└─────────────────────┘

┌─────────────────────┐         ┌─────────────────────┐
│   search_caches     │         │   recent_searches   │
├─────────────────────┤         ├─────────────────────┤
│ id (PK, UUID)       │         │ id (PK, UUID)       │
│ query (UNIQUE)      │         │ user_id (FK)        │
│ event_ids (JSON)    │         │ query               │
│ total_results       │         │ searched_at         │
│ search_time_seconds │         └─────────────────────┘
│ created_at          │                  ▲
│ expires_at          │                  │
└─────────────────────┘                  │
                                         │
                              users.id ──┘
```

---

## 테이블 상세

### 1. users

사용자 계정 및 프로필 정보

| 컬럼 | 타입 | 제약조건 | 설명 |
|------|------|----------|------|
| id | UUID | PK | 기본키 |
| email | VARCHAR(255) | UNIQUE, NOT NULL | 이메일 (로그인 식별자) |
| name | VARCHAR(100) | NOT NULL | 표시 이름 |
| profile_image | VARCHAR(500) | NULLABLE | 프로필 이미지 URL |
| provider | ENUM | NOT NULL | 인증 제공자 ('google', 'apple') |
| provider_id | VARCHAR(255) | NOT NULL | 제공자별 사용자 ID |
| notification_enabled | BOOLEAN | NOT NULL, DEFAULT true | 전체 알림 on/off |
| notification_new_event | BOOLEAN | NOT NULL, DEFAULT true | 새 행사 알림 |
| notification_ticket_open | BOOLEAN | NOT NULL, DEFAULT true | 티켓 오픈 알림 |
| notification_dday | BOOLEAN | NOT NULL, DEFAULT true | D-day 알림 |
| created_at | TIMESTAMPTZ | NOT NULL, DEFAULT now() | 생성 시각 |
| updated_at | TIMESTAMPTZ | NOT NULL, DEFAULT now() | 수정 시각 |

**인덱스**:
- `ix_users_email` (UNIQUE) - 이메일 검색

**ENUM Types**:
- `authprovider`: 'google', 'apple'

---

### 2. artists

아티스트/가수 정보

| 컬럼 | 타입 | 제약조건 | 설명 |
|------|------|----------|------|
| id | UUID | PK | 기본키 |
| name | VARCHAR(200) | NOT NULL | 아티스트명 (영문/원어) |
| name_ko | VARCHAR(200) | NULLABLE | 아티스트명 (한글) |
| image_url | VARCHAR(500) | NULLABLE | 프로필 이미지 URL |
| genre | VARCHAR(100) | NULLABLE | 장르 (K-POP, J-POP, Pop 등) |
| follower_count | INTEGER | NOT NULL, DEFAULT 0 | 팔로워 수 (캐시) |
| created_at | TIMESTAMPTZ | NOT NULL, DEFAULT now() | 생성 시각 |
| updated_at | TIMESTAMPTZ | NOT NULL, DEFAULT now() | 수정 시각 |

**인덱스**:
- `ix_artists_name` - 이름 검색

---

### 3. user_artists

사용자-아티스트 팔로우 관계 (다대다)

| 컬럼 | 타입 | 제약조건 | 설명 |
|------|------|----------|------|
| id | UUID | PK | 기본키 |
| user_id | UUID | FK, NOT NULL | 사용자 ID |
| artist_id | UUID | FK, NOT NULL | 아티스트 ID |
| created_at | TIMESTAMPTZ | NOT NULL, DEFAULT now() | 팔로우 시각 |

**외래키**:
- `user_id` → `users.id` (ON DELETE CASCADE)
- `artist_id` → `artists.id` (ON DELETE CASCADE)

**인덱스**:
- `ix_user_artists_user_id` - 사용자별 팔로우 목록
- `ix_user_artists_artist_id` - 아티스트별 팔로워 목록

**유니크 제약**:
- `uq_user_artist` (user_id, artist_id) - 중복 팔로우 방지

---

### 4. events

행사 정보 (콘서트, 팬미팅, 방송, 페스티벌)

| 컬럼 | 타입 | 제약조건 | 설명 |
|------|------|----------|------|
| id | UUID | PK | 기본키 |
| title | VARCHAR(500) | NOT NULL | 행사명 |
| category | ENUM | NOT NULL | 카테고리 ('concert', 'fanmeeting', 'broadcast', 'festival') |
| artist_id | UUID | FK, NOT NULL | 아티스트 ID |
| artist_name | VARCHAR(200) | NOT NULL | 아티스트명 (denormalized) |
| event_date | DATE | NOT NULL | 행사 날짜 |
| event_time | TIME | NULLABLE | 행사 시간 |
| timezone | VARCHAR(50) | NOT NULL, DEFAULT 'Asia/Seoul' | 타임존 |
| venue | VARCHAR(300) | NOT NULL | 장소명 |
| address | VARCHAR(500) | NULLABLE | 상세 주소 |
| city | VARCHAR(100) | NOT NULL | 도시 |
| country | VARCHAR(100) | NOT NULL | 국가 |
| price_currency | VARCHAR(10) | NULLABLE | 가격 통화 (KRW, JPY, USD 등) |
| price_min | NUMERIC(12,2) | NULLABLE | 최소 가격 |
| price_max | NUMERIC(12,2) | NULLABLE | 최대 가격 |
| price_tiers | JSON | NULLABLE | 좌석별 가격 [{name, price}] |
| image_url | VARCHAR(500) | NULLABLE | 행사 이미지 URL |
| ticket_url | VARCHAR(500) | NULLABLE | 예매 URL |
| source | VARCHAR(200) | NOT NULL | 정보 출처 도메인 |
| source_url | VARCHAR(500) | NOT NULL | 정보 출처 URL |
| collected_at | TIMESTAMPTZ | NOT NULL | RAG 수집 시각 |
| created_at | TIMESTAMPTZ | NOT NULL, DEFAULT now() | 생성 시각 |
| updated_at | TIMESTAMPTZ | NOT NULL, DEFAULT now() | 수정 시각 |

**외래키**:
- `artist_id` → `artists.id` (ON DELETE CASCADE)

**인덱스**:
- `ix_events_title` - 제목 검색
- `ix_events_category` - 카테고리 필터
- `ix_events_artist_id` - 아티스트별 행사
- `ix_events_event_date` - 날짜순 정렬/필터
- `ix_events_city` - 도시별 필터
- `ix_events_country` - 국가별 필터

**ENUM Types**:
- `eventcategory`: 'concert', 'fanmeeting', 'broadcast', 'festival'

---

### 5. event_embeddings

벡터 임베딩 (pgvector, RAG 검색용)

| 컬럼 | 타입 | 제약조건 | 설명 |
|------|------|----------|------|
| id | UUID | PK | 기본키 |
| event_id | UUID | FK, UNIQUE, NOT NULL | 행사 ID (1:1) |
| embedding | VECTOR(1536) | NOT NULL | OpenAI 임베딩 벡터 |
| embedded_text | VARCHAR(2000) | NOT NULL | 임베딩된 원본 텍스트 |
| model | VARCHAR(100) | NOT NULL, DEFAULT 'text-embedding-3-small' | 임베딩 모델명 |
| created_at | TIMESTAMPTZ | NOT NULL, DEFAULT now() | 생성 시각 |

**외래키**:
- `event_id` → `events.id` (ON DELETE CASCADE)

**인덱스**:
- `ix_event_embeddings_event_id` (UNIQUE) - 이벤트 조회
- `ix_event_embeddings_embedding` (IVFFlat, lists=100) - 벡터 유사도 검색

**pgvector 설정**:
- Extension: `CREATE EXTENSION IF NOT EXISTS vector`
- Index Type: IVFFlat (Approximate Nearest Neighbor)
- Distance Metric: Cosine similarity (`vector_cosine_ops`)

---

### 6. search_caches

RAG 검색 결과 캐시 (24시간 TTL)

| 컬럼 | 타입 | 제약조건 | 설명 |
|------|------|----------|------|
| id | UUID | PK | 기본키 |
| query | VARCHAR(500) | UNIQUE, NOT NULL | 검색 쿼리 (정규화됨) |
| event_ids | JSON | NOT NULL | 검색 결과 행사 ID 배열 |
| total_results | INTEGER | NOT NULL, DEFAULT 0 | 총 결과 수 |
| search_time_seconds | FLOAT | NOT NULL | 검색 소요 시간 (초) |
| created_at | TIMESTAMPTZ | NOT NULL, DEFAULT now() | 생성 시각 |
| expires_at | TIMESTAMPTZ | NOT NULL | 만료 시각 |

**인덱스**:
- `ix_search_caches_query` (UNIQUE) - 쿼리 조회
- `ix_search_caches_expires_at` - 만료 캐시 정리용

---

### 7. recent_searches

사용자별 최근 검색어 히스토리

| 컬럼 | 타입 | 제약조건 | 설명 |
|------|------|----------|------|
| id | UUID | PK | 기본키 |
| user_id | UUID | FK, NOT NULL | 사용자 ID |
| query | VARCHAR(500) | NOT NULL | 검색어 |
| searched_at | TIMESTAMPTZ | NOT NULL, DEFAULT now() | 검색 시각 |

**외래키**:
- `user_id` → `users.id` (ON DELETE CASCADE)

**인덱스**:
- `ix_recent_searches_user_id` - 사용자별 검색
- `ix_recent_searches_user_searched` (user_id, searched_at DESC) - 최근 검색 정렬

---

## 향후 추가 예정 테이블

### Phase 1

| 테이블 | 설명 | Feature |
|--------|------|---------|
| notifications | 알림 히스토리 | F4 |

### Phase 2+

| 테이블 | 설명 | Feature |
|--------|------|---------|
| posts | 팬 커뮤니티 게시물 | F6 |
| subscriptions | 프리미엄 구독 | F7 |

---

## 마이그레이션 히스토리

| 버전 | 날짜 | 설명 |
|------|------|------|
| 001_initial_auth | - | users, artists, user_artists 테이블 생성 |
| 002_add_events | - | events, event_embeddings, search_caches, recent_searches 테이블 생성 |

---

## 쿼리 예시

### 사용자가 팔로우한 아티스트 목록
```sql
SELECT a.*
FROM artists a
JOIN user_artists ua ON a.id = ua.artist_id
WHERE ua.user_id = :user_id
ORDER BY ua.created_at DESC;
```

### 아티스트의 팔로워 수 업데이트
```sql
UPDATE artists
SET follower_count = (
  SELECT COUNT(*) FROM user_artists WHERE artist_id = :artist_id
)
WHERE id = :artist_id;
```

### 아티스트 검색 (이름)
```sql
SELECT * FROM artists
WHERE name ILIKE '%' || :query || '%'
   OR name_ko ILIKE '%' || :query || '%'
ORDER BY follower_count DESC
LIMIT 20;
```

### 아티스트별 행사 목록 (날짜순)
```sql
SELECT e.*
FROM events e
WHERE e.artist_id = :artist_id
  AND e.event_date >= CURRENT_DATE
ORDER BY e.event_date ASC, e.event_time ASC;
```

### 벡터 유사도 검색 (Top 20)
```sql
SELECT e.*, ee.embedding <=> :query_embedding AS distance
FROM events e
JOIN event_embeddings ee ON e.id = ee.event_id
WHERE e.event_date >= CURRENT_DATE
ORDER BY ee.embedding <=> :query_embedding
LIMIT 20;
```

### 사용자 최근 검색어 (최신 10개)
```sql
SELECT * FROM recent_searches
WHERE user_id = :user_id
ORDER BY searched_at DESC
LIMIT 10;
```

### 만료된 검색 캐시 정리
```sql
DELETE FROM search_caches
WHERE expires_at < NOW();
```
