# F2: 아티스트 검색 & RAG

**Feature ID**: F2
**예상 기간**: 2주
**상태**: [status: completed]
**진행률**: Step 4/4 완료 (100%)

---

## 개요

RAG(Retrieval-Augmented Generation) 기반으로 아티스트의 행사 정보를 웹에서 수집하고, 검색 결과를 사용자에게 제공합니다. 검색 결과는 캐싱하여 재검색 시 빠르게 제공합니다.

## 범위

### 포함
- 아티스트 검색 UI (자동완성 + RAG 전체 검색)
- RAG 파이프라인 구현 (웹 검색 → LLM 추출 → 임베딩 → 벡터 저장)
- 검색 결과 캐싱 (24시간)
- 아티스트 프로필 화면 (행사 목록)
- 행사 상세 화면
- 카테고리별 필터 (콘서트/팬미팅/방송/페스티벌)

### 제외
- 티켓 예매 기능 (F5에서 구현)
- 캘린더 연동 (F3에서 구현)
- 푸시 알림 (F4에서 구현)

---

## 4-Step 구현 계획

### Step 1: UX Planning & Design [status: completed]

**Command**: `/ux-plan search-rag F2`

**작업 내용**:
1. PRD에서 AC 추출 (AC-F2-01 ~ AC-F2-03, US-4)
2. 사용자 여정 정의
   - Journey 1: RAG 검색으로 행사 찾기
   - Journey 2: 아티스트 프로필에서 행사 보기
   - Journey 3: 최근 검색/인기 아티스트로 빠른 접근
3. 화면 구조 설계 (탭 내 스택 네비게이션)
   - 검색 홈 (`/(tabs)/search`)
   - 검색 결과 (`/(tabs)/search?q={query}`)
   - 아티스트 프로필 (`/(tabs)/search/artist/[id]`)
   - 행사 상세 (`/(tabs)/search/event/[id]`)
4. AC ↔ 화면 매핑

**산출물**:
- `docs/ux/features/search-rag-flow.md` ✅
- `docs/ux/features/search-rag-screens.md` ✅

---

### Step 2: Frontend Prototype with Mock [status: completed]

**Command**: `/mock-ui search-rag F2`

**작업 내용**:
1. Mock 데이터 생성
   - 아티스트 목록 (이미지, 이름, 장르)
   - 행사 목록 (행사명, 날짜, 장소, 카테고리, 가격)
   - 검색 결과 (RAG 결과 시뮬레이션 - 3~5초 지연, 캐시 표시)
2. React Native 화면 구현
   - SearchScreen (검색 홈 + 자동완성 + 결과)
   - ArtistProfileScreen (행사 목록 + 관련 아티스트)
   - EventDetailScreen (disabled 버튼 포함)
3. 공통 컴포넌트 구현
   - EventCard
   - CategoryBadge
   - ArtistSearchInput (자동완성 + 웹 검색 옵션)
4. API Client (Mock Provider 패턴)

**산출물**:
- `apps/mobile/lib/mocks/search-rag.ts` ✅
- `apps/mobile/lib/api/search-api.ts` ✅
- `apps/mobile/app/(tabs)/search/_layout.tsx` ✅
- `apps/mobile/app/(tabs)/search/index.tsx` ✅
- `apps/mobile/app/(tabs)/search/artist/[id].tsx` ✅
- `apps/mobile/app/(tabs)/search/event/[id].tsx` ✅
- `apps/mobile/components/common/ArtistSearchInput.tsx` ✅
- `apps/mobile/components/search/EventCard.tsx` ✅
- `apps/mobile/components/search/CategoryBadge.tsx` ✅

---

### Step 3: Data Layer Design & Migration [status: completed]

**Command**: `/design-db search-rag F2`

**작업 내용**:
1. SQLAlchemy 모델 설계
   - Event 모델 (EventCategory ENUM 포함)
   - EventEmbedding 모델 (pgvector 1536차원)
   - SearchCache 모델
   - RecentSearch 모델
2. Alembic Migration 생성 (002_add_events)
3. pgvector IVFFlat 인덱스 설정

**산출물**:
- `apps/api/app/models/event.py` ✅
- `apps/api/app/models/embedding.py` ✅
- `apps/api/app/models/search.py` ✅
- `apps/api/alembic/versions/002_add_event_tables.py` ✅
- `docs/tech/db-schema.md` (업데이트) ✅

---

### Step 4: Backend API & Integration [status: completed]

**Command**: `/implement-api search-rag F2`

**작업 내용**:
1. RAG 파이프라인 구현
   - 웹 검색 (Tavily API) ✅
   - LLM 정보 추출 (GPT-4o-mini) ✅
   - 임베딩 생성 (OpenAI text-embedding-3-small) ✅
   - 벡터 저장/검색 (pgvector) ✅
2. FastAPI 라우터 구현 ✅
   - POST /api/v1/search (RAG 검색)
   - GET /api/v1/search/autocomplete (자동완성)
   - GET /api/v1/artists/{id}/events (아티스트 행사 목록)
   - GET /api/v1/artists/{id}/related (관련 아티스트)
   - GET /api/v1/events (행사 목록)
   - GET /api/v1/events/{id} (행사 상세)
   - GET/POST/DELETE /api/v1/search/recent (최근 검색어)
3. 캐싱 레이어 구현 (24시간 TTL) ✅
4. pytest API 테스트 ✅
5. Frontend API Client 업데이트 (Mock Provider 패턴) ✅

**산출물**:
- `apps/api/app/rag/crawler.py` ✅
- `apps/api/app/rag/extractor.py` ✅
- `apps/api/app/rag/embeddings.py` ✅
- `apps/api/app/rag/pipeline.py` ✅
- `apps/api/app/schemas/event.py` ✅
- `apps/api/app/schemas/search.py` ✅
- `apps/api/app/services/event.py` ✅
- `apps/api/app/services/search.py` ✅
- `apps/api/app/services/recent_search.py` ✅
- `apps/api/app/routers/events.py` ✅
- `apps/api/app/routers/search.py` ✅
- `apps/api/tests/test_events.py` ✅
- `apps/api/tests/test_search.py` ✅
- `apps/mobile/lib/api/search-api.ts` (업데이트) ✅
- `docs/tech/api-spec.md` ✅

---

## Acceptance Criteria

- [x] 아티스트 검색 시 5초 이내 결과 반환, 캐시 시 즉시 (AC-F2-01) ✅
- [x] 검색 결과에 행사 정보 포함 (AC-F2-02) ✅
- [x] 24시간 내 캐시된 결과 재사용 (AC-F2-03) ✅

---

## 기술 노트

### RAG 파이프라인

```
사용자 검색어
    │
    ▼
웹 검색 (Tavily API)
    │
    ▼
LLM 정보 추출 (GPT-4)
    │  - 행사명, 날짜, 장소, 카테고리 추출
    │  - 신뢰도 점수 부여
    ▼
임베딩 생성 (text-embedding-3-small)
    │
    ▼
벡터 저장 (pgvector)
    │
    ▼
결과 반환 + 캐싱
```

### 카테고리 분류
- 콘서트 (concert)
- 팬미팅 (fanmeeting)
- 방송 (broadcast)
- 페스티벌 (festival)

### 캐싱 전략
- 검색 결과를 24시간 캐싱
- 동일 검색어 → 캐시 히트 시 즉시 반환
- 캐시 무효화: 수동 새로고침 시
