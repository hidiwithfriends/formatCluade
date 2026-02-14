# F3: 행사 캘린더

**Feature ID**: F3
**예상 기간**: 2주
**상태**: [status: in-progress]
**진행률**: Step 1/4 완료 (25%)

---

## 개요

팔로우한 아티스트의 행사를 캘린더 형식으로 확인하고 관리하는 기능입니다. 월간/주간/일간 뷰를 제공하며, 아티스트별 필터와 로컬 캘린더 연동을 지원합니다.

## 범위

### 포함
- 월간/주간/일간 캘린더 뷰
- 팔로우 아티스트 필터
- 행사 상세 페이지 (캘린더 내 네비게이션)
- 로컬 캘린더 연동 (선택 기능)
- 행사 날짜 도트 표시 (카테고리별 색상)

### 제외
- 행사 알림 (F4에서 구현)
- 티켓 예매 (F5에서 구현)
- 캘린더 위젯 (Phase 2)

---

## 4-Step 구현 계획

### Step 1: UX Planning & Design [status: completed]

**Command**: `/ux-plan calendar F3`

**작업 내용**:
1. PRD에서 AC 추출 (AC-F3-01 ~ AC-F3-03, US-2)
2. 사용자 여정 정의
   - Journey 1: 캘린더에서 행사 확인
   - Journey 2: 뷰 모드 변경
   - Journey 3: 아티스트 필터 적용
   - Journey 4: 로컬 캘린더에 추가
3. 화면 구조 설계
   - 캘린더 메인 (`/(tabs)/calendar`)
   - 필터 바텀시트
   - 행사 상세 (기존 화면 재사용)
4. AC ↔ 화면 매핑

**산출물**:
- `docs/ux/features/calendar-flow.md` ✅
- `docs/ux/features/calendar-screens.md` ✅

---

### Step 2: Frontend Prototype with Mock [status: todo]

**Command**: `/mock-ui calendar F3`

**작업 내용**:
1. Mock 데이터 생성
   - 캘린더용 행사 데이터 (날짜별 그룹핑)
   - 팔로우 아티스트 목록
2. React Native 화면 구현
   - CalendarScreen (월간/주간/일간 뷰)
   - ArtistFilterSheet (바텀시트)
   - 행사 상세 (기존 EventDetailScreen 재사용)
3. 공통 컴포넌트 구현
   - CalendarView (뷰 모드 통합)
   - MonthView / WeekView / DayView
   - CalendarHeader
   - DayCell, EventDot
   - DayEventList
   - ArtistFilterSheet

**산출물 (예정)**:
- `apps/mobile/lib/mocks/calendar.ts`
- `apps/mobile/lib/api/calendar-api.ts`
- `apps/mobile/app/(tabs)/calendar/_layout.tsx`
- `apps/mobile/app/(tabs)/calendar/index.tsx`
- `apps/mobile/components/calendar/CalendarView.tsx`
- `apps/mobile/components/calendar/MonthView.tsx`
- `apps/mobile/components/calendar/WeekView.tsx`
- `apps/mobile/components/calendar/DayView.tsx`
- `apps/mobile/components/calendar/CalendarHeader.tsx`
- `apps/mobile/components/calendar/DayCell.tsx`
- `apps/mobile/components/calendar/EventDot.tsx`
- `apps/mobile/components/calendar/DayEventList.tsx`
- `apps/mobile/components/calendar/ArtistFilterSheet.tsx`

---

### Step 3: Data Layer Design & Migration [status: todo]

**Command**: `/design-db calendar F3`

**작업 내용**:
1. 캘린더 관련 추가 모델 검토
   - 기존 Event 모델 재사용 (F2에서 생성)
   - 추가 필요한 모델 없음 (API 쿼리로 해결)
2. 인덱스 최적화
   - 날짜 범위 쿼리 인덱스 확인

**산출물 (예정)**:
- (기존 모델 재사용, 추가 작업 최소화)
- `docs/tech/db-schema.md` (필요시 업데이트)

---

### Step 4: Backend API & Integration [status: todo]

**Command**: `/implement-api calendar F3`

**작업 내용**:
1. 캘린더 전용 API 엔드포인트
   - GET /api/v1/calendar/events (날짜 범위 + 아티스트 필터)
   - GET /api/v1/calendar/events/summary (날짜별 행사 수)
2. 기존 Events API 활용
   - GET /api/v1/events (from_date, to_date, artist_ids 파라미터)
3. pytest API 테스트
4. Frontend API 연동 (Mock → Real)

**산출물 (예정)**:
- `apps/api/app/routers/calendar.py`
- `apps/api/app/services/calendar.py`
- `apps/api/app/schemas/calendar.py`
- `apps/api/tests/test_calendar.py`
- `apps/mobile/lib/api/calendar-api.ts` (업데이트)

---

## Acceptance Criteria

- [ ] 캘린더에서 행사 날짜 표시 (AC-F3-01)
- [ ] 필터로 특정 아티스트만 표시 (AC-F3-02)
- [ ] 행사 탭하면 상세 정보 표시 (AC-F3-03)

---

## 기술 노트

### 캘린더 라이브러리

React Native에서 캘린더 구현 옵션:

1. **직접 구현** (권장)
   - 완전한 커스터마이즈 가능
   - UI 테마 일관성 유지
   - 복잡도: 중간

2. **react-native-calendars**
   - 빠른 구현
   - 커스터마이즈 제한적
   - 의존성 추가

→ 직접 구현 권장 (UI 일관성, 복잡한 도트 표시 필요)

### 뷰 모드 상태 관리

```typescript
type CalendarViewMode = 'month' | 'week' | 'day';

interface CalendarState {
  viewMode: CalendarViewMode;
  selectedDate: Date;
  events: Map<string, Event[]>;  // "2026-03-15" -> events
  filteredArtistIds: string[];
}
```

### 날짜 범위 쿼리 최적화

- 월간 뷰: 전월 마지막 주 ~ 다음월 첫 주 포함 (6주)
- 주간 뷰: 해당 주 7일
- 일간 뷰: 해당 일 1일 (프리페치: 전후 1일)

### 로컬 캘린더 연동

```typescript
import * as Calendar from 'expo-calendar';

async function addEventToCalendar(event: Event) {
  const { status } = await Calendar.requestCalendarPermissionsAsync();
  if (status !== 'granted') return;

  const calendars = await Calendar.getCalendarsAsync(Calendar.EntityTypes.EVENT);
  const defaultCalendar = calendars.find(c => c.isPrimary) || calendars[0];

  await Calendar.createEventAsync(defaultCalendar.id, {
    title: event.title,
    startDate: new Date(`${event.date}T${event.time}`),
    endDate: new Date(`${event.date}T${event.time}`).setHours(+3),
    location: event.venue,
    notes: `예매: ${event.ticketUrl}`,
  });
}
```

---

## 의존성

- **F1 (인증)**: 팔로우 아티스트 목록 필요
- **F2 (검색 & RAG)**: Event 모델 재사용, 행사 데이터

---

## UI 참고

### 벤치마크 앱
- Apple Calendar (월간/일간 뷰 전환)
- Google Calendar (색상 도트)
- Fantastical (자연스러운 스와이프)

### 핵심 UX 원칙
1. 행사가 있는 날짜를 한눈에 파악
2. 빠른 뷰 모드 전환
3. 직관적인 필터 적용
