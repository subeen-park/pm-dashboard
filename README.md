![wbs](https://github.com/user-attachments/assets/3879ac94-de18-46dd-a096-12275cff2294)



# WBS Release Manager v2

## 구조
```
wbs-v2/
├── backend/          # Flask API 서버
│   ├── app.py
│   ├── requirements.txt
│   └── data/
│       ├── projects.json       # WBS 프로젝트 목록
│       ├── tasks/{id}.json     # 프로젝트별 태스크
│       ├── webhook.json
│       └── logs.json
└── frontend/         # Vue 3 (Options API)
    └── src/
        ├── App.vue              # GNB + 화면 전환
        ├── api/index.js         # API 모듈
        ├── utils.js
        └── components/
            ├── WBSList.vue      # 목록 (검색 + 페이지네이션)
            ├── WBSDetail.vue    # 상세 (탭 구조)
            ├── ProjectForm.vue  # WBS 등록/수정 모달
            ├── TaskTable.vue    # 태스크 테이블
            ├── GanttChart.vue
            ├── NotifPanel.vue
            └── TaskForm.vue
```

## 실행
```bash
# 백엔드
cd backend && pip install -r requirements.txt && python app.py

# 프론트엔드
cd frontend && npm install && npm run dev
```

브라우저: http://localhost:3000
