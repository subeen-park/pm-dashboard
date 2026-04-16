# PM Suite

**PM 업무를 한 곳에서 끝내는 릴리즈 관리 도구**

🔗 **[https://wbs-release-manager.vercel.app](https://wbs-release-manager.vercel.app)**

---

## 개요

PM Suite는 게임/앱 프로덕트 PM을 위한 풀스택 릴리즈 관리 대시보드입니다. WBS 관리, 릴리즈 캘린더, 머지 트래킹, Jira 정체 분석까지 팀의 모든 일정을 하나의 화면에서 관리할 수 있습니다.

---

## 주요 기능

### WBS 보드
- 프로젝트 등록 및 태스크 그룹별 관리
- 태스크 진행률, 담당자, 시작일/마감일 추적
- **D-7 리스크 뱃지** — 마감 7일 이내 태스크 자동 표시
- **지연 스티키 네비게이터** — 지연/리스크/진행중 태스크 순환 포커싱
- **드래그앤드롭** — 태스크를 다른 그룹으로 이동
- **진행률 일괄 수정** — 모든 태스크 진행률을 모달 한 화면에서 수정
- **태스크 상세 팝업** — 태스크명/메모 클릭 시 전체 내용 팝업
- 간트 차트 (1주/1개월/전체 뷰)

### 엑셀/Google Sheets 업로드
- `.xlsx` / `.csv` 파일 업로드로 태스크 일괄 등록
- Google Sheets URL 붙여넣기로 직접 가져오기
- 업로드 전 기존 데이터 교체 확인 모달
- **자동 백업** — 업로드/삭제 전 스냅샷 자동 저장, 이전 시점 원복 가능
- 그룹명 자동 정규화 (`기획팀 → 기획`, `BE팀 → 개발(BE)` 등)

### 릴리즈 캘린더
- 전체 프로젝트 마감일을 월별 캘린더로 시각화
- 상태별 색상 구분 (완료/진행중/리스크/지연/대기)
- 날짜 클릭 시 해당 일의 프로젝트 목록 사이드 패널

### 머지 트래커
- 브랜치/버전별 머지 현황 추적
- 미빌드 / 빌드완료 / 머지요청완료 / 머지완료 단계 관리
- 메트릭 카드 클릭 시 해당 탭으로 즉시 포커싱
- 데모 모드 지원

### Jira 레이더
- Jira 티켓의 정체 구간 분석 (정체기간 기준 필터)
- **병목 담당자 Top 10** — 담당자별 정체 건수 카드 + 막대 그래프
- 기한 누락 / 기한 지연 티켓 별도 탭 관리
- 담당자 / 업무유형 필터
- 메트릭 카드 클릭 시 해당 섹션으로 스크롤 이동

### WBS 목록
- 최신/오래된/마감일/이름순 정렬
- 등록일 컬럼 표시
- **다중 선택 삭제** — 체크박스로 여러 WBS 한번에 삭제
- 상태 필터 (진행중/리스크/지연/완료/대기)

---

## 기술 스택

| 구분 | 기술 |
|------|------|
| 프론트엔드 | Vue 3 (Options API), Vite |
| 백엔드 | Flask (Python 3.11) |
| 데이터베이스 | PostgreSQL (Render) |
| 프론트 배포 | Vercel |
| 백엔드 배포 | Render |
| 폰트 | Noto Sans KR, DM Mono |

---

## 프로젝트 구조

```
pm-dashboard/
├── backend/
│   ├── app.py              # Flask API + PostgreSQL
│   └── requirements.txt
└── frontend/
    └── src/
        ├── App.vue              # GNB + 홈 랜딩 + 라우팅
        ├── api/index.js
        ├── utils.js             # 상태 계산, 그룹 정규화 유틸
        └── components/
            ├── WBSList.vue          # 프로젝트 목록
            ├── WBSDetail.vue        # 프로젝트 상세 + 업로드
            ├── TaskTable.vue        # 태스크 테이블 + 드래그앤드롭
            ├── GanttChart.vue       # 간트 차트
            ├── TaskForm.vue         # 태스크 등록/수정 폼
            ├── ProjectForm.vue      # 프로젝트 등록/수정 폼
            ├── MergeTracker.vue     # 머지 트래커
            ├── JiraRadar.vue        # Jira 정체 분석
            ├── ReleaseCalendar.vue  # 릴리즈 캘린더
            ├── ReleaseChecklist.vue # 릴리즈 체크리스트
            └── NotifPanel.vue       # 알림 설정
```

---

## 로컬 실행

### 백엔드

```bash
cd backend
pip install -r requirements.txt
FLASK_APP=app.py flask run
```

### 프론트엔드

```bash
cd frontend
npm install
npm run dev
```

`.env` 파일에 API URL 설정:

```
VITE_API_URL=http://localhost:5000/api
```

---

## 배포 환경

| 항목 | 값 |
|------|------|
| 프론트엔드 | Vercel (main 브랜치 자동 배포) |
| 백엔드 | Render (Python 3.11, gunicorn) |
| DB | Render PostgreSQL |
| 슬립 방지 | UptimeRobot 5분 핑 |

### 환경변수 (Render)

```
DATABASE_URL=<Render PostgreSQL Internal URL>
```

### 환경변수 (Vercel)

```
VITE_API_URL=https://wbs-release-manager.onrender.com/api
```

---

## 엑셀 업로드 양식

WBS 보드 내 **업로드 ▾ → 업로드 양식 다운받기** 에서 CSV 템플릿을 받을 수 있어요.

| 컬럼 | 설명 | 예시 |
|------|------|------|
| Group | 그룹명 | 기획 |
| Task | 태스크명 | 기획서 작성 |
| Subtask | 하위 태스크 | 요구사항 정의 |
| Note | 메모 | - |
| JIRA | Jira 티켓 번호 | PROJ-001 |
| Team | 팀명 | 기획팀 |
| Assignee | 담당자 | 박수빈 |
| Start Date | 시작일 | 2025-10-17 |
| End Date | 마감일 | 2025-10-27 |
| Progress | 진행률 (0~100) | 80 |

---

## 데이터베이스 테이블

```sql
projects        -- WBS 프로젝트
tasks           -- 태스크
task_snapshots  -- 업로드/삭제 전 자동 백업
webhook         -- 웹훅 설정
logs            -- 활동 로그
```

---

## 개발자

**박수빈** — [@subeen-park](https://github.com/subeen-park)
