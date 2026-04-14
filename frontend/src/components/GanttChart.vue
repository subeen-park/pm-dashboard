<template>
  <div>
    <!-- 네비게이션 + 기간 선택 -->
    <div class="gantt-nav">
      <div class="period-btns">
        <button v-for="p in PERIODS" :key="p.key"
          class="period-btn" :class="{on: period===p.key}" @click="setPeriod(p.key)">
          {{ p.label }}
        </button>
      </div>
      <div class="nav-center">
        <button class="nav-btn" @click="prev">← 이전</button>
        <span class="range">{{ rangeLabel }}</span>
        <button class="nav-btn" @click="next">다음 →</button>
      </div>
      <button class="nav-btn" @click="goToday">오늘</button>
    </div>

    <div class="gantt-wrap">
      <div v-if="!tasks.length" class="empty-state">태스크가 없습니다</div>
      <div v-else style="overflow-x:auto">
        <!-- 날짜 헤더 -->
        <div class="g-row g-header">
          <div class="g-label-head">태스크</div>
          <div v-for="(d,i) in dates" :key="d"
            class="g-day-head"
            :style="{ width: CW+'px', minWidth: CW+'px' }"
            :class="{ today: d===todayStr, 'week-start': isMonday(d) }">
            <span class="day-num">{{ fmtDay(d) }}</span>
          </div>
        </div>

        <!-- 태스크 행 -->
        <div v-for="t in tasks" :key="t.id" class="g-row">
          <div class="g-label">
            <span class="gb" :style="groupStyle(t.group)">{{ t.group }}</span>
            <span class="g-task-name">{{ t.task }}</span>
          </div>
          <template v-for="(d,i) in dates" :key="d">
            <div v-if="isStart(t,i)"
              class="g-bar-cell"
              :style="{ width: barW(t)+'px', minWidth: barW(t)+'px' }">
              <div class="g-bar" :style="barStyle(t.group)">{{ t.task }}</div>
            </div>
            <div v-else-if="!inBar(t,i)"
              class="g-empty"
              :style="{ width: CW+'px', minWidth: CW+'px' }"
              :class="{ today: d===todayStr, 'week-start': isMonday(d) }">
            </div>
          </template>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { today, getStatus } from '../utils.js'

const PERIODS = [
  { key: 'week',  label: '1주일', days: 7  },
  { key: 'month', label: '1개월', days: 30 },
  { key: 'all',   label: '전체',  days: 0  },
]

// 그룹별 고정 색상 — 라이트/다크 모드 모두 대응
const GROUP_PALETTE = {
  '기획':    { bg: '#dbeafe', color: '#1e40af', border: '#93c5fd' },
  '디자인':  { bg: '#ede9fe', color: '#5b21b6', border: '#c4b5fd' },
  '개발(BE)':{ bg: '#dcfce7', color: '#166534', border: '#86efac' },
  '개발(FE)':{ bg: '#fef9c3', color: '#854d0e', border: '#fde047' },
  'Android': { bg: '#ffedd5', color: '#9a3412', border: '#fdba74' },
  'iOS':     { bg: '#cffafe', color: '#155e75', border: '#67e8f9' },
  'QA':      { bg: '#fce7f3', color: '#9d174d', border: '#f9a8d4' },
}

const DEFAULT_PALETTE = { bg: '#f1f5f9', color: '#475569', border: '#cbd5e1' }

function makeDate(offset) {
  const d = new Date(); d.setDate(d.getDate() + offset)
  return d.toISOString().slice(0, 10)
}

export default {
  name: 'GanttChart',
  props: { tasks: { type: Array, default: () => [] } },
  data() {
    return {
      period: 'month',
      offset: 0,
      todayStr: today(),
      PERIODS,
      CW: 28,
    }
  },
  computed: {
    days() {
      if (this.period === 'week')  return 7
      if (this.period === 'month') return 30
      // 전체: 가장 이른 시작일~가장 늦은 마감일
      if (!this.tasks.length) return 30
      const starts = this.tasks.map(t => t.startDate).filter(Boolean)
      const ends   = this.tasks.map(t => t.endDate).filter(Boolean)
      if (!starts.length || !ends.length) return 30
      const minD = starts.reduce((a,b) => a < b ? a : b)
      const maxD = ends.reduce((a,b) => a > b ? a : b)
      const diff = Math.round((new Date(maxD) - new Date(minD)) / 86400000) + 1
      return Math.max(diff, 7)
    },
    startDt() {
      if (this.period === 'all' && this.tasks.length) {
        const starts = this.tasks.map(t => t.startDate).filter(Boolean)
        if (starts.length) {
          const min = starts.reduce((a,b) => a < b ? a : b)
          const d = new Date(min); d.setDate(d.getDate() + this.offset * this.days)
          return d.toISOString().slice(0, 10)
        }
      }
      const d = new Date(); d.setDate(d.getDate() + this.offset * this.days)
      return d.toISOString().slice(0, 10)
    },
    dates() {
      return Array.from({ length: this.days }, (_, i) => {
        const d = new Date(this.startDt); d.setDate(d.getDate() + i)
        return d.toISOString().slice(0, 10)
      })
    },
    rangeLabel() {
      if (!this.dates.length) return ''
      const s = this.dates[0].slice(5).replace('-', '/')
      const e = this.dates[this.dates.length - 1].slice(5).replace('-', '/')
      return `${s} ~ ${e}`
    },
  },
  methods: {
    setPeriod(p) { this.period = p; this.offset = 0 },
    prev()    { this.offset-- },
    next()    { this.offset++ },
    goToday() { this.offset = 0 },
    isMonday(d) { return new Date(d).getDay() === 1 },
    fmtDay(d) {
      const dt = new Date(d)
      if (this.period === 'week') return `${dt.getMonth()+1}/${dt.getDate()}`
      return `${dt.getDate()}`
    },
    si(t) { return Math.max(0, Math.round((new Date(t.startDate || this.dates[0]) - new Date(this.dates[0])) / 86400000)) },
    ei(t) { return Math.min(this.days - 1, Math.round((new Date(t.endDate || this.dates[this.days - 1]) - new Date(this.dates[0])) / 86400000)) },
    isStart(t, i) { return i === this.si(t) && i <= this.ei(t) },
    inBar(t, i)   { return i > this.si(t) && i <= this.ei(t) },
    barW(t)       { return Math.max(1, this.ei(t) - this.si(t) + 1) * this.CW },
    barStyle(group) {
      const p = GROUP_PALETTE[group] || DEFAULT_PALETTE
      return { background: p.bg, color: p.color, border: `1px solid ${p.border}` }
    },
    groupStyle(group) {
      const p = GROUP_PALETTE[group] || DEFAULT_PALETTE
      return { background: p.bg, color: p.color, border: `1px solid ${p.border}` }
    },
  }
}
</script>

<style scoped>
.gantt-nav { display:flex; align-items:center; gap:12px; margin-bottom:12px; flex-wrap:wrap }
.period-btns { display:flex; gap:4px }
.period-btn  { padding:4px 12px; border-radius:6px; border:1px solid var(--border2); background:transparent; color:var(--muted); font-size:12px; cursor:pointer; font-family:inherit; transition:all .15s }
.period-btn.on { background:var(--bg4); color:var(--text); border-color:var(--border) }
.nav-center { display:flex; align-items:center; gap:8px; flex:1; justify-content:center }
.nav-btn    { padding:4px 10px; border-radius:6px; border:1px solid var(--border2); background:transparent; color:var(--muted); font-size:12px; cursor:pointer; font-family:inherit }
.nav-btn:hover { background:var(--bg3); color:var(--text) }
.range      { font-size:12px; color:var(--muted); min-width:150px; text-align:center }

.gantt-wrap { background:var(--bg2); border:1px solid var(--border); border-radius:10px; overflow:hidden }

/* 헤더 행 */
.g-header    { background:var(--bg3); border-bottom:1px solid var(--border) }
.g-label-head{ width:180px; min-width:180px; border-right:1px solid var(--border); padding:7px 10px; font-size:11px; color:var(--muted); display:flex; align-items:center }
.g-day-head  { border-right:1px solid var(--border); display:flex; align-items:center; justify-content:center; padding:6px 0 }
.g-day-head.today { background:rgba(245,158,11,.12) }
.g-day-head.week-start { background:var(--bg3) }
.day-num     { font-size:10px; color:var(--muted) }
.g-day-head.today .day-num { color:var(--amber); font-weight:600 }

/* 태스크 행 */
.g-row     { display:flex; border-bottom:1px solid var(--border); min-height:36px; align-items:stretch }
.g-row:last-child { border-bottom:none }
.g-label   { width:180px; min-width:180px; border-right:1px solid var(--border); padding:7px 10px; display:flex; align-items:center; gap:6px; overflow:hidden }
.g-task-name{ font-size:11px; color:var(--text); overflow:hidden; text-overflow:ellipsis; white-space:nowrap }

/* 빈 셀 */
.g-empty   { border-right:1px solid var(--border); height:36px }
.g-empty.today { background:rgba(245,158,11,.06) }
.g-empty.week-start { background:var(--bg3) }

/* 바 셀 */
.g-bar-cell { display:flex; align-items:center; padding:8px 3px }
.g-bar      { height:20px; border-radius:4px; display:flex; align-items:center; padding:0 8px; font-size:10px; font-weight:500; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; width:100% }
.bar-done { background:#dcfce7; color:#166534; border:1px solid #86efac }
.bar-prog { background:#dbeafe; color:#1e40af; border:1px solid #93c5fd }
.bar-risk { background:#fef9c3; color:#854d0e; border:1px solid #fde047 }
.bar-over { background:#fee2e2; color:#991b1b; border:1px solid #fca5a5 }
.bar-pend { background:#f1f5f9; color:#64748b; border:1px solid #cbd5e1 }

/* 그룹 뱃지 */
.gb { display:inline-block; padding:1px 6px; border-radius:4px; font-size:9px; font-weight:600; flex-shrink:0; white-space:nowrap }

.empty-state { text-align:center; padding:40px; color:var(--muted); font-size:13px }
</style>