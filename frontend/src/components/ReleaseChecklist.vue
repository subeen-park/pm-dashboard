<template>
  <div class="cl-page">
    <div class="cl-topbar">
      <div>
        <h2 class="cl-title">✅ 릴리즈 체크리스트</h2>
        <p class="cl-desc">릴리즈 전 필수 확인 항목을 팀별로 체크하세요. 항목을 클릭해 완료 처리할 수 있습니다.</p>
      </div>
      <button class="btn btn-primary" @click="showNewBoard = true">+ 새 체크리스트</button>
    </div>

    <!-- 보드 없을 때 -->
    <div v-if="boards.length === 0" class="empty-hero">
      <div class="empty-icon">📋</div>
      <div class="empty-title">체크리스트가 없습니다</div>
      <div class="empty-desc">릴리즈 버전별 체크리스트를 만들어 팀과 함께 진행 상황을 공유하세요.</div>
      <button class="btn btn-primary" @click="showNewBoard = true">+ 첫 체크리스트 만들기</button>
    </div>

    <!-- 보드 목록 -->
    <div v-else class="boards-grid">
      <div v-for="board in boards" :key="board.id" class="board-card"
        :class="{ 'board-done': boardProgress(board) === 100 }">
        <div class="board-card-header">
          <div class="board-header-left">
            <div class="board-version">{{ board.version }}</div>
            <div class="board-name">{{ board.name }}</div>
            <div class="board-date" v-if="board.date">🗓 {{ board.date }}</div>
          </div>
          <div class="board-header-right">
            <div class="progress-ring-wrap">
              <svg class="progress-ring" width="52" height="52" viewBox="0 0 52 52">
                <circle class="ring-bg" cx="26" cy="26" r="22" />
                <circle class="ring-fill" cx="26" cy="26" r="22"
                  :stroke-dasharray="ringDash(board)"
                  :stroke-dashoffset="ringOffset(board)"
                  :stroke="boardProgress(board) === 100 ? 'var(--green)' : 'var(--amber)'" />
              </svg>
              <span class="ring-pct">{{ boardProgress(board) }}%</span>
            </div>
          </div>
        </div>

        <!-- 카테고리별 체크 항목 -->
        <div class="board-categories">
          <div v-for="cat in board.categories" :key="cat.name" class="cat-section">
            <div class="cat-header">
              <span class="cat-icon">{{ cat.icon }}</span>
              <span class="cat-name">{{ cat.name }}</span>
              <span class="cat-progress">{{ cat.items.filter(i=>i.checked).length }}/{{ cat.items.length }}</span>
            </div>
            <div class="cat-items">
              <div v-for="item in cat.items" :key="item.id"
                class="check-item" :class="{ checked: item.checked }"
                @click="toggleItem(board, cat, item)">
                <div class="check-box">
                  <svg v-if="item.checked" viewBox="0 0 16 16" width="12" height="12" fill="currentColor">
                    <path d="M13.854 3.646a.5.5 0 0 1 0 .708l-7 7a.5.5 0 0 1-.708 0l-3.5-3.5a.5.5 0 1 1 .708-.708L6.5 10.293l6.646-6.647a.5.5 0 0 1 .708 0z"/>
                  </svg>
                </div>
                <div class="check-content">
                  <div class="check-label">{{ item.label }}</div>
                  <div class="check-meta" v-if="item.assignee || item.checked">
                    <span v-if="item.assignee" class="check-assignee">{{ item.assignee }}</span>
                    <span v-if="item.checked" class="check-done-label">완료</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="board-footer">
          <button class="footer-btn" @click="duplicateBoard(board)">복제</button>
          <button class="footer-btn danger" @click="deleteBoard(board.id)">삭제</button>
          <div class="board-done-badge" v-if="boardProgress(board) === 100">🎉 완료!</div>
        </div>
      </div>
    </div>

    <!-- 새 체크리스트 모달 -->
    <div v-if="showNewBoard" class="overlay" @click.self="showNewBoard = false">
      <div class="modal">
        <div class="modal-title">📋 새 릴리즈 체크리스트</div>
        <p class="modal-desc">릴리즈 버전과 이름을 입력하면 기본 체크리스트 템플릿이 생성됩니다.</p>
        <div class="field">
          <label>버전 (예: v2.1.0)</label>
          <input v-model="newVersion" placeholder="v2.1.0" />
        </div>
        <div class="field">
          <label>릴리즈명</label>
          <input v-model="newName" placeholder="2024년 1월 정기 릴리즈" />
        </div>
        <div class="field">
          <label>릴리즈 예정일</label>
          <input type="date" v-model="newDate" />
        </div>
        <div class="field">
          <label>템플릿</label>
          <div class="template-options">
            <div v-for="tmpl in TEMPLATES" :key="tmpl.key"
              class="tmpl-option" :class="{ selected: selectedTemplate === tmpl.key }"
              @click="selectedTemplate = tmpl.key">
              <div class="tmpl-icon">{{ tmpl.icon }}</div>
              <div class="tmpl-name">{{ tmpl.name }}</div>
            </div>
          </div>
        </div>
        <div class="modal-actions">
          <button class="btn btn-ghost" @click="showNewBoard = false">취소</button>
          <button class="btn btn-primary" @click="createBoard" :disabled="!newVersion.trim()">만들기</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
const CIRC = 2 * Math.PI * 22  // circumference of r=22

const TEMPLATE_DATA = {
  standard: [
    {
      name: 'QA / 테스트', icon: '🧪',
      items: [
        { label: '기능 테스트 완료', assignee: 'QA' },
        { label: '회귀 테스트 완료', assignee: 'QA' },
        { label: '크로스 브라우저 테스트', assignee: 'QA' },
        { label: '모바일 환경 테스트', assignee: 'QA' },
        { label: '성능/부하 테스트', assignee: 'QA' },
      ]
    },
    {
      name: '개발 완료', icon: '💻',
      items: [
        { label: '코드 리뷰 완료', assignee: '개발' },
        { label: 'PR 머지 완료', assignee: '개발' },
        { label: '빌드 성공 확인', assignee: '개발' },
        { label: 'API 문서 업데이트', assignee: '개발' },
      ]
    },
    {
      name: '배포 준비', icon: '🚀',
      items: [
        { label: '스테이징 배포 확인', assignee: 'DevOps' },
        { label: '환경 변수 확인', assignee: 'DevOps' },
        { label: 'DB 마이그레이션 검토', assignee: 'DevOps' },
        { label: '롤백 플랜 수립', assignee: 'DevOps' },
        { label: '배포 알림 전송', assignee: 'PM' },
      ]
    },
    {
      name: '이해관계자 확인', icon: '👥',
      items: [
        { label: 'PM 최종 승인', assignee: 'PM' },
        { label: '디자인 QA 완료', assignee: '디자인' },
        { label: '비즈니스 요구사항 충족 확인', assignee: 'PM' },
      ]
    },
  ],
  hotfix: [
    {
      name: '긴급 수정 확인', icon: '🔥',
      items: [
        { label: '이슈 재현 및 원인 분석', assignee: '개발' },
        { label: '핫픽스 코드 리뷰', assignee: '개발' },
        { label: '핫픽스 빌드 확인', assignee: '개발' },
        { label: '영향 범위 분석', assignee: '개발' },
      ]
    },
    {
      name: '빠른 QA', icon: '⚡',
      items: [
        { label: '핵심 기능 스모크 테스트', assignee: 'QA' },
        { label: '수정 사항 검증', assignee: 'QA' },
      ]
    },
    {
      name: '긴급 배포', icon: '🚨',
      items: [
        { label: 'PM / CTO 승인', assignee: 'PM' },
        { label: '스테이징 확인', assignee: 'DevOps' },
        { label: '배포 및 모니터링', assignee: 'DevOps' },
        { label: '롤백 대기', assignee: 'DevOps' },
      ]
    },
  ],
  app: [
    {
      name: 'iOS', icon: '🍎',
      items: [
        { label: 'iOS 빌드 (Release)', assignee: 'iOS 개발' },
        { label: 'TestFlight 배포', assignee: 'iOS 개발' },
        { label: 'App Store 심사 제출', assignee: 'iOS 개발' },
        { label: '심사 통과 확인', assignee: 'iOS 개발' },
      ]
    },
    {
      name: 'Android', icon: '🤖',
      items: [
        { label: 'Android 빌드 (Release)', assignee: 'AOS 개발' },
        { label: '내부 테스트 배포', assignee: 'AOS 개발' },
        { label: 'Play Store 심사 제출', assignee: 'AOS 개발' },
        { label: '심사 통과 확인', assignee: 'AOS 개발' },
      ]
    },
    {
      name: '공통 QA', icon: '🧪',
      items: [
        { label: '기능 테스트 완료', assignee: 'QA' },
        { label: '디바이스 크로스 테스트', assignee: 'QA' },
        { label: 'PM 최종 승인', assignee: 'PM' },
      ]
    },
  ]
}

const TEMPLATES = [
  { key: 'standard', icon: '🌐', name: '웹 릴리즈' },
  { key: 'app',      icon: '📱', name: '앱 릴리즈' },
  { key: 'hotfix',   icon: '🔥', name: '핫픽스' },
]

let nextId = Date.now()
function makeId() { return ++nextId }

function makeBoard(version, name, date, templateKey) {
  return {
    id: makeId(),
    version,
    name,
    date,
    categories: TEMPLATE_DATA[templateKey].map(cat => ({
      name: cat.name,
      icon: cat.icon,
      items: cat.items.map(item => ({
        id: makeId(),
        label: item.label,
        assignee: item.assignee,
        checked: false,
      }))
    }))
  }
}

export default {
  name: 'ReleaseChecklist',
  data() {
    return {
      boards: [],
      showNewBoard: false,
      newVersion: '',
      newName: '',
      newDate: '',
      selectedTemplate: 'standard',
      TEMPLATES,
    }
  },
  mounted() {
    const saved = localStorage.getItem('release-checklists')
    if (saved) {
      try { this.boards = JSON.parse(saved) } catch(e) {}
    }
  },
  methods: {
    save() {
      localStorage.setItem('release-checklists', JSON.stringify(this.boards))
    },
    boardProgress(board) {
      let total = 0, done = 0
      board.categories.forEach(cat => {
        total += cat.items.length
        done += cat.items.filter(i => i.checked).length
      })
      return total === 0 ? 0 : Math.round(done / total * 100)
    },
    ringDash()   { return `${CIRC} ${CIRC}` },
    ringOffset(board) {
      const pct = this.boardProgress(board) / 100
      return CIRC * (1 - pct)
    },
    toggleItem(board, cat, item) {
      item.checked = !item.checked
      this.save()
    },
    createBoard() {
      if (!this.newVersion.trim()) return
      const board = makeBoard(
        this.newVersion.trim(),
        this.newName.trim() || this.newVersion.trim() + ' 릴리즈',
        this.newDate,
        this.selectedTemplate
      )
      this.boards.unshift(board)
      this.save()
      this.showNewBoard = false
      this.newVersion = ''; this.newName = ''; this.newDate = ''
      this.selectedTemplate = 'standard'
    },
    duplicateBoard(board) {
      const copy = JSON.parse(JSON.stringify(board))
      copy.id = makeId()
      copy.version = copy.version + ' (복사)'
      copy.categories.forEach(cat => {
        cat.items.forEach(item => { item.id = makeId(); item.checked = false })
      })
      this.boards.unshift(copy)
      this.save()
    },
    deleteBoard(id) {
      if (!confirm('이 체크리스트를 삭제하시겠습니까?')) return
      this.boards = this.boards.filter(b => b.id !== id)
      this.save()
    },
  }
}
</script>

<style scoped>
.cl-page { padding: 24px; max-width: 1400px; margin: 0 auto }
.cl-topbar { display: flex; align-items: flex-start; justify-content: space-between; gap: 16px; margin-bottom: 28px }
.cl-title  { font-size: 20px; font-weight: 700; color: var(--text); margin-bottom: 4px }
.cl-desc   { font-size: 13px; color: var(--muted) }

.btn { display: inline-flex; align-items: center; gap: 6px; padding: 9px 18px; border-radius: 8px; font-size: 14px; font-family: inherit; cursor: pointer; border: none; font-weight: 500; transition: all .15s }
.btn-primary { background: var(--amber); color: #0a0800 }.btn-primary:hover { background: #f0b85a }
.btn-ghost   { background: transparent; color: var(--muted); border: 1px solid var(--border2) }.btn-ghost:hover { background: var(--bg3) }
.btn:disabled { opacity: .5; cursor: not-allowed }

/* 빈 상태 */
.empty-hero  { text-align: center; padding: 80px 20px; display: flex; flex-direction: column; align-items: center; gap: 14px }
.empty-icon  { font-size: 48px }
.empty-title { font-size: 18px; font-weight: 700; color: var(--text) }
.empty-desc  { font-size: 14px; color: var(--muted); line-height: 1.7; max-width: 400px }

/* 보드 그리드 */
.boards-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(380px, 1fr)); gap: 20px }

.board-card { background: var(--bg2); border: 1px solid var(--border); border-radius: 14px; overflow: hidden; transition: box-shadow .2s }
.board-card:hover { box-shadow: 0 4px 20px rgba(0,0,0,.1) }
.board-done { border-color: var(--green) }

.board-card-header { display: flex; align-items: flex-start; justify-content: space-between; padding: 18px 20px 14px; border-bottom: 1px solid var(--border) }
.board-header-left  { flex: 1; min-width: 0 }
.board-version { font-size: 11px; font-family: 'DM Mono', monospace; font-weight: 700; color: var(--amber); margin-bottom: 3px }
.board-name   { font-size: 15px; font-weight: 700; color: var(--text); margin-bottom: 4px }
.board-date   { font-size: 12px; color: var(--muted) }
.board-header-right { flex-shrink: 0; display: flex; align-items: center }

/* 링 차트 */
.progress-ring-wrap { position: relative; display: flex; align-items: center; justify-content: center }
.progress-ring { transform: rotate(-90deg); overflow: visible }
.ring-bg   { fill: none; stroke: var(--bg4); stroke-width: 4 }
.ring-fill { fill: none; stroke-width: 4; stroke-linecap: round; transition: stroke-dashoffset .5s ease }
.ring-pct  { position: absolute; font-size: 11px; font-weight: 700; font-family: 'DM Mono', monospace; color: var(--text) }

/* 카테고리 */
.board-categories { padding: 14px 20px; display: flex; flex-direction: column; gap: 14px }
.cat-section { }
.cat-header { display: flex; align-items: center; gap: 6px; margin-bottom: 6px }
.cat-icon   { font-size: 14px }
.cat-name   { font-size: 12px; font-weight: 700; color: var(--text); flex: 1 }
.cat-progress { font-size: 11px; color: var(--muted); font-family: 'DM Mono', monospace }
.cat-items  { display: flex; flex-direction: column; gap: 3px }

.check-item { display: flex; align-items: flex-start; gap: 10px; padding: 7px 10px; border-radius: 8px; cursor: pointer; transition: background .12s; border: 1px solid transparent }
.check-item:hover { background: var(--bg3) }
.check-item.checked { opacity: .65 }
.check-item.checked .check-label { text-decoration: line-through }

.check-box { width: 18px; height: 18px; border: 1.5px solid var(--border2); border-radius: 5px; display: flex; align-items: center; justify-content: center; flex-shrink: 0; margin-top: 1px; transition: all .15s }
.check-item.checked .check-box { background: var(--green); border-color: var(--green); color: #fff }
.check-content { flex: 1; min-width: 0 }
.check-label   { font-size: 13px; color: var(--text); line-height: 1.4 }
.check-meta    { display: flex; align-items: center; gap: 6px; margin-top: 2px }
.check-assignee  { font-size: 11px; color: var(--muted) }
.check-done-label{ font-size: 11px; color: var(--green); font-weight: 600 }

/* 카드 푸터 */
.board-footer { display: flex; align-items: center; gap: 8px; padding: 12px 20px; border-top: 1px solid var(--border); background: var(--bg3) }
.footer-btn   { background: none; border: 1px solid var(--border2); color: var(--muted); font-size: 12px; padding: 4px 12px; border-radius: 6px; cursor: pointer; font-family: inherit; transition: all .15s }
.footer-btn:hover { background: var(--bg4); color: var(--text) }
.footer-btn.danger { color: var(--red); border-color: var(--red-dim) }
.footer-btn.danger:hover { background: var(--red-dim) }
.board-done-badge { margin-left: auto; font-size: 12px; font-weight: 700; color: var(--green) }

/* 모달 */
.overlay { position: fixed; inset: 0; background: rgba(0,0,0,.5); z-index: 300; display: flex; align-items: center; justify-content: center }
.modal   { background: var(--bg2); border: 1px solid var(--border2); border-radius: 14px; padding: 28px; width: 480px; max-width: 90vw }
.modal-title { font-size: 16px; font-weight: 700; margin-bottom: 6px; color: var(--text) }
.modal-desc  { font-size: 13px; color: var(--muted); margin-bottom: 18px; line-height: 1.6 }
.field       { margin-bottom: 14px }
.field label { display: block; font-size: 11px; color: var(--muted); margin-bottom: 5px; font-weight: 600; text-transform: uppercase; letter-spacing: .04em }
.field input  { width: 100%; background: var(--bg3); border: 1px solid var(--border2); border-radius: 8px; padding: 9px 12px; color: var(--text); font-size: 13px; font-family: inherit; outline: none }
.field input:focus { border-color: var(--amber) }
.modal-actions { display: flex; justify-content: flex-end; gap: 8px; margin-top: 20px }

.template-options { display: flex; gap: 10px }
.tmpl-option { flex: 1; background: var(--bg3); border: 1.5px solid var(--border2); border-radius: 10px; padding: 12px; text-align: center; cursor: pointer; transition: all .15s }
.tmpl-option:hover { border-color: var(--amber) }
.tmpl-option.selected { border-color: var(--amber); background: var(--amber-dim) }
.tmpl-icon { font-size: 22px; margin-bottom: 5px }
.tmpl-name { font-size: 12px; font-weight: 600; color: var(--text) }
</style>
