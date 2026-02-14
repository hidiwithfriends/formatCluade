# Phase 1: MVP 상세 계획

## 개요

**목표**: 핵심 기능을 갖춘 최소 실행 가능 제품 출시
**기간**: 8-10주
**상태**: [status: in-progress]
**진행률**: 40% (F1 완료, F2 완료)

---

## 개발 원칙

이 Phase는 **UI-First Mock-Driven Development** 방식을 따릅니다:

1. **UX 설계가 먼저** (Backend 전에 Frontend)
2. **Mock 데이터로 Frontend 완성**
3. **Mock → Real API 전환 최소화**

각 Feature는 4단계 프로세스를 따릅니다:
- Step 1: UX Planning & Design (`/ux-plan`)
- Step 2: Frontend Prototype with Mock (`/mock-ui`)
- Step 3: Data Layer Design & Migration (`/design-db`)
- Step 4: Backend API & Integration (`/implement-api`)

---

## Feature 목록

### F1: 인증 & 유저 프로필 [status: completed]

**예상 기간**: 1.5주
**상세 계획**: `docs/project/features/f1-auth.md`

**범위**:
- 소셜 로그인 (Google, Apple)
- 관심 아티스트 선택 (온보딩)
- 푸시 알림 설정
- 프로필 관리

**의존성**: 없음

**Step 진행 상황**:
- [x] Step 1: UX Planning & Design ✅
- [x] Step 2: Frontend Prototype with Mock ✅
- [x] Step 3: Data Layer Design & Migration ✅
- [x] Step 4: Backend API & Integration ✅

---

### F2: 아티스트 검색 & RAG [status: completed]

**예상 기간**: 2주
**상세 계획**: `docs/project/features/f2-search-rag.md`

**범위**:
- 아티스트 검색 UI
- RAG 파이프라인 구현
  - 웹 검색 (Tavily API)
  - 정보 추출 (GPT-4o-mini)
  - 임베딩 생성 (OpenAI Embeddings)
  - 벡터 저장 (pgvector)
- 검색 결과 캐싱 (24시간 TTL)

**의존성**: F1 (인증)

**Step 진행 상황**:
- [x] Step 1: UX Planning & Design ✅
- [x] Step 2: Frontend Prototype with Mock ✅
- [x] Step 3: Data Layer Design & Migration ✅
- [x] Step 4: Backend API & Integration ✅

---

### F3: 행사 캘린더 [status: in-progress]

**예상 기간**: 2주
**상세 계획**: `docs/project/features/f3-calendar.md`

**범위**:
- 월간/주간/일간 캘린더 뷰
- 관심 아티스트 필터
- 행사 상세 페이지
- 로컬 캘린더 연동 (선택)

**의존성**: F1 (인증), F2 (검색)

**Step 진행 상황**:
- [x] Step 1: UX Planning & Design ✅
- [ ] Step 2: Frontend Prototype with Mock
- [ ] Step 3: Data Layer Design & Migration
- [ ] Step 4: Backend API & Integration

---

### F4: 푸시 알림 [status: todo]

**예상 기간**: 1주
**상세 계획**: `docs/project/features/f4-notifications.md`

**범위**:
- Expo Notifications 연동
- 새 행사 알림
- 티켓 오픈 알림
- 행사 D-day 알림
- 알림 설정 관리

**의존성**: F1 (인증), F2 (검색)

---

### F5: 티켓 예매 연동 [status: todo]

**예상 기간**: 1.5주
**상세 계획**: `docs/project/features/f5-ticketing.md`

**범위**:
- 예매 사이트 링크 표시
- 가격 정보 표시
- 예매 오픈 일정 표시
- 외부 브라우저 연동

**의존성**: F2 (검색), F3 (캘린더)

---

## Feature 간 의존성

```
F1: 인증 & 유저 프로필
    ↓
F2: 아티스트 검색 & RAG
    ↓
F3: 행사 캘린더 ← F4: 푸시 알림
    ↓
F5: 티켓 예매 연동
```

---

## 타임라인

| 주차 | Feature | Step |
|------|---------|------|
| 1-2 | F1 | Step 1-4 |
| 3-4 | F2 | Step 1-4 |
| 5-6 | F3 | Step 1-4 |
| 7 | F4 | Step 1-4 |
| 8-9 | F5 | Step 1-4 |
| 10 | QA & 배포 | - |

---

## 완료 조건

Phase 1이 완료되려면:

- [ ] F1-F5 모든 Feature가 `[status: completed]`
- [ ] E2E 테스트 통과율 90% 이상
- [ ] 앱스토어/플레이스토어 심사 제출
- [ ] 100명 초기 사용자 피드백 수집

---

## 다음 단계

Phase 1 완료 후:
1. 사용자 피드백 분석
2. Phase 2 상세 계획 작성
3. roadmap.md에서 Phase 1을 `[status: done]`으로 변경
