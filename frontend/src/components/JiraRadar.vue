<template>
  <div class="page">
    <!-- 상단 필터 바 -->
    <div class="filter-bar">
      <div class="filter-group">
        <span class="filter-label">위험 기준</span>
        <select v-model.number="riskThreshold" class="filter-select">
          <option v-for="d in [1,2,3,5,7,10,14]" :key="d" :value="d">{{ d }}일 이상</option>
        </select>
      </div>
      <div class="filter-group">
        <span class="filter-label">담당자</span>
        <select v-model="selectedAssignee" class="filter-select">
          <option value="">전체</option>
          <option v-for="a in allAssignees" :key="a">{{ a }}</option>
        </select>
      </div>
      <div class="filter-group" style="margin-left:auto">
        <label class="demo-toggle">
          <input type="checkbox" v-model="isDemo" />
          <span class="demo-label">데모 모드</span>
        </label>
      </div>
    </div>

    <!-- 메트릭 -->
    <div class="metrics">
      <div class="mc">
        <div class="mc-label">총 관리 대상</div>
        <div class="mc-val" style="color:var(--blue)">{{ displayData.length }}</div>
      </div>
      <div class="mc mc-clickable" @click="scrollTo('aging-section')" title="정체 탭으로 이동">
        <div class="mc-label">⚠️ 정체 리스크 <span class="mc-arrow">↓</span></div>
        <div class="mc-val" style="color:var(--yellow)">{{ highRiskData.length }}</div>
        <div class="mc-sub">{{ riskThreshold }}일 이상 정체</div>
      </div>
      <div class="mc mc-clickable" @click="scrollTo('aging-section')" title="정체 탭으로 이동">
        <div class="mc-label">최대 정체 <span class="mc-arrow">↓</span></div>
        <div class="mc-val" style="color:var(--red)"><span class="mc-num">{{ maxAging }}</span><span class="mc-unit">일</span></div>
      </div>
      <div class="mc mc-clickable" @click="scrollTo('due-section')" title="일정 리스크 탭으로 이동">
        <div class="mc-label">기한 누락 <span class="mc-arrow">↓</span></div>
        <div class="mc-val" style="color:var(--muted)">{{ missingDueData.length }}</div>
      </div>
      <div class="mc mc-clickable" @click="scrollTo('due-section')" title="일정 리스크 탭으로 이동">
        <div class="mc-label">기한 지연 <span class="mc-arrow">↓</span></div>
        <div class="mc-val" style="color:var(--red)">{{ overdueData.length }}</div>
      </div>
    </div>

    <!-- Top 10 병목 담당자 -->
    <div class="section-title">🏆 병목 담당자 Top 10</div>
    <div class="top10-grid">
      <div v-for="(item, i) in top10" :key="item.name"
        class="top10-card"
        :class="{selected: detailAssignee===item.name}"
        @click="toggleDetail(item.name)">
        <div class="top10-rank">{{ i+1 }}</div>
        <div class="top10-info">
          <div class="top10-name">{{ item.name }}</div>
          <div class="top10-count">🚨 {{ item.count }}건</div>
        </div>
        <div class="top10-arrow">{{ detailAssignee===item.name ? '▲' : '▼' }}</div>
      </div>
    </div>

    <!-- 상세 패널 -->
    <div v-if="detailAssignee" class="detail-panel">
      <div class="detail-header">
        <span>👤 {{ detailAssignee }} 정체 티켓</span>
        <button class="close-btn" @click="detailAssignee=null">✕</button>
      </div>
      <table class="data-table">
        <thead><tr><th>티켓번호</th><th>요약</th><th>현재상태</th><th style="width:90px">정체(일)</th><th style="width:70px">링크</th></tr></thead>
        <tbody>
          <tr v-for="r in detailRows" :key="r.티켓번호" class="data-row">
            <td class="cell-mono">{{ r.티켓번호 }}</td>
            <td class="cell-text">{{ r.요약 }}</td>
            <td><span class="s-chip" :class="stateClass(r.현재상태)">{{ r.현재상태 }}</span></td>
            <td><span class="aging-badge" :class="agingClass(r['정체기간(일)'])">{{ r['정체기간(일)'] }}일</span></td>
            <td><a :href="r.링크" target="_blank" class="link-btn">열기 ↗</a></td>
          </tr>
        </tbody>
      </table>
    </div>

    <div class="divider"></div>

    <!-- 탭 -->
    <div class="tabs">
      <div class="tab" :class="{on:activeTab==='aging'}" @click="activeTab='aging'">
        ⏳ 정체 티켓 <span class="tab-cnt">{{ highRiskData.length }}</span>
      </div>
      <div class="tab" :class="{on:activeTab==='due'}" @click="activeTab='due'">
        🚨 일정 리스크 <span class="tab-cnt">{{ missingDueData.length + overdueData.length }}</span>
      </div>
    </div>

    <!-- 정체 탭 -->
    <div v-if="activeTab==='aging'" id="aging-section">
      <!-- 업무유형 필터 -->
      <div class="type-tabs">
        <button v-for="t in issueTypes" :key="t"
          class="type-btn" :class="{on: activeType===t}" @click="activeType=t">
          {{ t }} ({{ typeCount(t) }})
        </button>
      </div>

      <div class="table-wrap">
        <table class="data-table">
          <thead>
            <tr><th style="width:100px">티켓번호</th><th>요약</th><th style="width:100px">담당자</th><th style="width:100px">현재상태</th><th style="width:90px">정체(일)</th><th style="width:70px">링크</th></tr>
          </thead>
          <tbody>
            <tr v-if="!agingFiltered.length"><td colspan="6" class="empty-state">정체 티켓이 없습니다</td></tr>
            <tr v-for="r in agingFiltered" :key="r.티켓번호" class="data-row">
              <td class="cell-mono">{{ r.티켓번호 }}</td>
              <td class="cell-text">{{ r.요약 }}</td>
              <td class="cell-text muted">{{ r.담당자 }}</td>
              <td><span class="s-chip" :class="stateClass(r.현재상태)">{{ r.현재상태 }}</span></td>
              <td><span class="aging-badge" :class="agingClass(r['정체기간(일)'])">{{ r['정체기간(일)'] }}일</span></td>
              <td><a :href="r.링크" target="_blank" class="link-btn">열기 ↗</a></td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- 바 차트 (순수 CSS) -->
      <div class="chart-section">
        <div class="section-title" style="margin-bottom:12px">📊 업무유형별 병목 현황</div>
        <div class="bar-chart">
          <div v-for="item in chartData" :key="item.type" class="bar-row">
            <div class="bar-type">{{ item.type }}</div>
            <div class="bar-track">
              <div class="bar-fill" :style="{width: (item.count/chartMax*100)+'%'}"></div>
            </div>
            <div class="bar-num">{{ item.count }}건</div>
          </div>
        </div>
      </div>
    </div>

    <!-- 일정 리스크 탭 -->
    <div v-if="activeTab==='due'" id="due-section">
      <div class="sub-section" id="missing-section">
        <div class="sub-title">기한 누락 작업 ({{ missingDueData.length }}건)</div>
        <div class="table-wrap">
          <table class="data-table">
            <thead><tr><th>티켓번호</th><th>요약</th><th style="width:100px">담당자</th><th style="width:70px">링크</th></tr></thead>
            <tbody>
              <tr v-if="!missingDueData.length"><td colspan="4" class="empty-state">누락된 티켓이 없습니다 ✓</td></tr>
              <tr v-for="r in missingDueData" :key="r.티켓번호" class="data-row">
                <td class="cell-mono">{{ r.티켓번호 }}</td>
                <td class="cell-text">{{ r.요약 }}</td>
                <td class="cell-text muted">{{ r.담당자 }}</td>
                <td><a :href="r.링크" target="_blank" class="link-btn">열기 ↗</a></td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <div class="sub-section" id="overdue-section">
        <div class="sub-title">기한 지연 작업 ({{ overdueData.length }}건)</div>
        <div class="table-wrap">
          <table class="data-table">
            <thead><tr><th>티켓번호</th><th>요약</th><th style="width:100px">담당자</th><th style="width:100px">기한</th><th style="width:70px">링크</th></tr></thead>
            <tbody>
              <tr v-if="!overdueData.length"><td colspan="5" class="empty-state">지연된 티켓이 없습니다 ✓</td></tr>
              <tr v-for="r in overdueData" :key="r.티켓번호" class="data-row">
                <td class="cell-mono">{{ r.티켓번호 }}</td>
                <td class="cell-text">{{ r.요약 }}</td>
                <td class="cell-text muted">{{ r.담당자 }}</td>
                <td class="cell-mono" style="color:var(--red)">{{ r.기한 }}</td>
                <td><a :href="r.링크" target="_blank" class="link-btn">열기 ↗</a></td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
const MOCK = [
  {업무유형:'버그',티켓번호:'DEMO-101',요약:'[결제] 특정 환경에서 결제 버튼 미노출',담당자:'강대리',현재상태:'대기','정체기간(일)':15,기한:'2026-04-01',지연여부:'지연 됨 ❌',링크:'#'},
  {업무유형:'작업',티켓번호:'DEMO-102',요약:'[UI/UX] 메인 페이지 배너 리뉴얼',담당자:'이주임',현재상태:'진행 중','정체기간(일)':7,기한:'2026-06-15',지연여부:'정상',링크:'#'},
  {업무유형:'개선',티켓번호:'DEMO-103',요약:'[서버] API 응답 속도 최적화',담당자:'박팀장',현재상태:'확인/수정 중','정체기간(일)':5,기한:'누락 🚨',지연여부:'-',링크:'#'},
  {업무유형:'에픽',티켓번호:'DEMO-104',요약:'[신규] 2분기 시즌 패스 시스템',담당자:'김사원',현재상태:'접수 대기','정체기간(일)':3,기한:'2026-07-20',지연여부:'정상',링크:'#'},
  {업무유형:'버그',티켓번호:'DEMO-105',요약:'[AOS] 특정 단말기 앱 무한 로딩',담당자:'최주임',현재상태:'대기','정체기간(일)':12,기한:'2026-03-31',지연여부:'지연 됨 ❌',링크:'#'},
  {업무유형:'하위 작업',티켓번호:'DEMO-106',요약:'상점 아이템 아이콘 리소스 제작',담당자:'정대리',현재상태:'진행 중','정체기간(일)':8,기한:'2026-04-10',지연여부:'지연 됨 ❌',링크:'#'},
  {업무유형:'작업',티켓번호:'DEMO-107',요약:'[인프라] DB 서버 스토리지 증설',담당자:'홍팀장',현재상태:'확인/수정 중','정체기간(일)':4,기한:'누락 🚨',지연여부:'-',링크:'#'},
  {업무유형:'개선',티켓번호:'DEMO-108',요약:'[웹] 커뮤니티 게시판 검색 고도화',담당자:'박사원',현재상태:'진행 예정','정체기간(일)':6,기한:'2026-06-30',지연여부:'정상',링크:'#'},
  {업무유형:'버그',티켓번호:'DEMO-109',요약:'[iOS] 푸시 알림 간헐적 미발송',담당자:'최주임',현재상태:'대기','정체기간(일)':10,기한:'2026-04-05',지연여부:'지연 됨 ❌',링크:'#'},
  {업무유형:'작업',티켓번호:'DEMO-110',요약:'[기획] 랭킹 시스템 밸런스 조정안',담당자:'김사원',현재상태:'진행 중','정체기간(일)':2,기한:'2026-07-01',지연여부:'정상',링크:'#'},
  {업무유형:'버그',티켓번호:'DEMO-111',요약:'[결제] 환불 처리 지연 건 개선',담당자:'강대리',현재상태:'대기','정체기간(일)':9,기한:'2026-04-20',지연여부:'정상',링크:'#'},
  {업무유형:'에픽',티켓번호:'DEMO-112',요약:'신규 캐릭터 시스템 설계',담당자:'이주임',현재상태:'접수 대기','정체기간(일)':11,기한:'누락 🚨',지연여부:'-',링크:'#'},
]

export default {
  name: 'JiraRadar',
  data() {
    return {
      isDemo: true, riskThreshold: 3,
      selectedAssignee: '', activeTab: 'aging',
      activeType: '전체', detailAssignee: null,
    }
  },
  computed: {
    displayData() { return MOCK },
    highRiskData() {
      let d = this.displayData.filter(r => r['정체기간(일)'] >= this.riskThreshold)
      if (this.selectedAssignee) d = d.filter(r => r.담당자 === this.selectedAssignee)
      return d
    },
    missingDueData() { return this.displayData.filter(r => r.기한 === '누락 🚨') },
    overdueData()    { return this.displayData.filter(r => r.지연여부 === '지연 됨 ❌') },
    maxAging()       { return Math.max(...this.displayData.map(r => r['정체기간(일)']), 0) },
    allAssignees()   { return [...new Set(this.displayData.map(r => r.담당자))].sort() },
    top10() {
      const counts = {}
      this.highRiskData.forEach(r => { counts[r.담당자] = (counts[r.담당자]||0)+1 })
      return Object.entries(counts).sort((a,b)=>b[1]-a[1]).slice(0,10).map(([name,count])=>({name,count}))
    },
    detailRows() {
      if (!this.detailAssignee) return []
      return this.highRiskData.filter(r => r.담당자 === this.detailAssignee).sort((a,b)=>b['정체기간(일)']-a['정체기간(일)'])
    },
    issueTypes() { return ['전체', ...[...new Set(this.highRiskData.map(r=>r.업무유형))].sort()] },
    agingFiltered() {
      let d = this.highRiskData
      if (this.activeType !== '전체') d = d.filter(r=>r.업무유형===this.activeType)
      return d.sort((a,b)=>b['정체기간(일)']-a['정체기간(일)'])
    },
    chartData() {
      const types = [...new Set(this.displayData.map(r=>r.업무유형))]
      return types.map(t=>({ type:t, count:this.displayData.filter(r=>r.업무유형===t).length })).sort((a,b)=>b.count-a.count)
    },
    chartMax() { return Math.max(...this.chartData.map(c=>c.count), 1) },
  },
  methods: {
    scrollTo(id) {
      const tabKey = (id === 'missing-section' || id === 'overdue-section' || id === 'due-section') ? 'due' : 'aging'
      this.activeTab = tabKey
      this.$nextTick(() => {
        setTimeout(() => {
          const el = document.getElementById(id)
          if (el) el.scrollIntoView({ behavior: 'smooth', block: 'start' })
        }, 50)
      })
    },
    toggleDetail(name) { this.detailAssignee = this.detailAssignee===name ? null : name },
    typeCount(t) { return t==='전체' ? this.highRiskData.length : this.highRiskData.filter(r=>r.업무유형===t).length },
    stateClass(s) {
      if (s==='진행 중')  return 'sc-progress'
      if (s==='대기')     return 'sc-wait'
      if (s.includes('수정')) return 'sc-fix'
      return 'sc-other'
    },
    agingClass(d) {
      if (d >= 10) return 'ag-high'
      if (d >= 5)  return 'ag-mid'
      return 'ag-low'
    },
  }
}
</script>

<style scoped>
.page { padding:20px 24px }

.filter-bar { display:flex; align-items:center; gap:16px; flex-wrap:wrap; background:var(--bg2); border:1px solid var(--border); border-radius:10px; padding:12px 16px; margin-bottom:16px }
.filter-label { font-size:11px; color:var(--muted); white-space:nowrap }
.filter-group { display:flex; align-items:center; gap:8px }
.slider { width:120px; accent-color:var(--amber) }
.threshold-val { font-size:12px; font-weight:600; color:var(--amber); font-family:'DM Mono',monospace; white-space:nowrap }
.filter-select { background:var(--bg3); border:1px solid var(--border2); border-radius:6px; padding:5px 8px; color:var(--text); font-size:12px; outline:none }
.filter-select option { background:var(--bg2) }
.demo-toggle { display:flex; align-items:center; gap:6px; cursor:pointer; font-size:12px }
.demo-toggle input { accent-color:var(--amber) }
.demo-label { color:var(--muted) }

.metrics { display:grid; grid-template-columns:repeat(5,1fr); gap:10px; margin-bottom:16px }
.mc      { background:var(--bg2); border:1px solid var(--border); border-radius:10px; padding:14px 16px }
.mc-label{ font-size:11px; color:var(--muted); text-transform:uppercase; letter-spacing:.05em; margin-bottom:4px }
.mc-val  { font-size:24px; font-weight:600; display:flex; align-items:baseline; gap:2px }
.mc-num  { font-family:'DM Mono',monospace }
.mc-unit { font-family:'Noto Sans KR',sans-serif; font-size:16px }
.mc-sub  { font-size:11px; color:var(--muted); margin-top:3px }
.mc-arrow{ font-size:11px }
.mc-clickable { cursor:pointer; transition:all .15s; user-select:none }
.mc-clickable:hover { filter:brightness(.95) }
.mc-clickable:active { transform:scale(.98) }

.section-title { font-size:13px; font-weight:600; color:var(--text); margin-bottom:10px }

.top10-grid { display:grid; grid-template-columns:repeat(5,1fr); gap:8px; margin-bottom:16px }
.top10-card { background:var(--bg2); border:1px solid var(--border); border-radius:8px; padding:10px 12px; display:flex; align-items:center; gap:8px; cursor:pointer; transition:all .15s }
.top10-card:hover { background:var(--bg3) }
.top10-card.selected { border-color:var(--amber); background:var(--bg3) }
.top10-rank { font-size:18px; font-weight:700; color:var(--muted); font-family:'DM Mono',monospace; min-width:20px }
.top10-info { flex:1; overflow:hidden }
.top10-name { font-size:13px; font-weight:500; white-space:nowrap; overflow:hidden; text-overflow:ellipsis }
.top10-count{ font-size:11px; color:var(--red); margin-top:2px }
.top10-arrow{ font-size:10px; color:var(--muted) }

.detail-panel { background:var(--bg2); border:1px solid var(--amber); border-radius:10px; margin-bottom:16px; overflow:hidden }
.detail-header { display:flex; align-items:center; justify-content:space-between; padding:10px 14px; background:var(--bg3); border-bottom:1px solid var(--border); font-size:13px; font-weight:600 }
.close-btn { background:none; border:none; color:var(--muted); cursor:pointer; font-size:14px; padding:2px 6px; border-radius:4px }
.close-btn:hover { color:var(--text); background:var(--bg4) }

.divider { border:none; border-top:1px solid var(--border); margin:16px 0 }

.tabs  { display:flex; gap:2px; background:var(--bg2); border:1px solid var(--border); border-radius:8px; padding:3px; width:fit-content; margin-bottom:14px }
.tab   { padding:6px 16px; border-radius:6px; cursor:pointer; font-size:13px; color:var(--muted); transition:all .15s; display:flex; align-items:center; gap:6px }
.tab.on{ background:var(--bg4); color:var(--text) }
.tab-cnt { background:var(--bg3); color:var(--muted); font-size:11px; padding:1px 6px; border-radius:10px; font-family:'DM Mono',monospace }
.tab.on .tab-cnt { background:var(--bg2); color:var(--text) }

.type-tabs { display:flex; gap:4px; flex-wrap:wrap; margin-bottom:12px }
.type-btn  { padding:4px 12px; border-radius:6px; border:1px solid var(--border2); background:transparent; color:var(--muted); font-size:12px; cursor:pointer; font-family:inherit; transition:all .15s }
.type-btn.on { background:var(--bg4); color:var(--text); border-color:var(--border) }

.table-wrap { background:var(--bg2); border:1px solid var(--border); border-radius:10px; overflow:hidden; margin-bottom:16px }
.data-table { width:100%; border-collapse:collapse }
.data-table th { background:var(--bg3); padding:9px 12px; text-align:left; font-size:11px; font-weight:600; color:var(--muted); border-bottom:1px solid var(--border); white-space:nowrap }
.data-table td { padding:9px 12px; border-bottom:1px solid var(--border); vertical-align:middle }
.data-table tr:last-child td { border-bottom:none }
.data-row:hover td { background:var(--bg3) }
.cell-text { font-size:13px; color:var(--text) }
.cell-mono { font-size:12px; font-family:'DM Mono',monospace }
.muted { color:var(--muted) }
.empty-state { text-align:center; padding:30px; color:var(--muted); font-size:13px }

.s-chip { display:inline-block; padding:2px 8px; border-radius:5px; font-size:11px; font-weight:600 }
.sc-progress { background:var(--blue-dim); color:var(--blue) }
.sc-wait     { background:var(--bg4); color:var(--muted) }
.sc-fix      { background:var(--yellow-dim); color:var(--yellow) }
.sc-other    { background:var(--bg4); color:var(--muted) }

.aging-badge { display:inline-block; padding:2px 8px; border-radius:5px; font-size:11px; font-weight:600; font-family:'DM Mono',monospace }
.ag-high { background:var(--red-dim); color:var(--red) }
.ag-mid  { background:var(--yellow-dim); color:var(--yellow) }
.ag-low  { background:var(--green-dim); color:var(--green) }

.link-btn { color:var(--blue); text-decoration:none; font-size:12px; font-weight:500 }
.link-btn:hover { text-decoration:underline }

.chart-section { background:var(--bg2); border:1px solid var(--border); border-radius:10px; padding:16px; margin-bottom:16px }
.bar-chart { display:flex; flex-direction:column; gap:10px }
.bar-row   { display:flex; align-items:center; gap:10px }
.bar-type  { width:80px; font-size:12px; color:var(--muted); text-align:right; flex-shrink:0 }
.bar-track { flex:1; height:18px; background:var(--bg4); border-radius:4px; overflow:hidden }
.bar-fill  { height:100%; background:var(--amber); border-radius:4px; transition:width .4s }
.bar-num   { width:40px; font-size:12px; font-family:'DM Mono',monospace; color:var(--muted) }

.sub-section { margin-bottom:16px }
.sub-title   { font-size:13px; font-weight:600; margin-bottom:8px; color:var(--text) }

@media(max-width:900px) { .metrics { grid-template-columns:repeat(3,1fr) }; .top10-grid { grid-template-columns:repeat(2,1fr) } }
</style>