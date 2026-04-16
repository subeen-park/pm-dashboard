<template>
  <div class="cal-page">
    <div class="cal-topbar">
      <div class="cal-title-area">
        <h2 class="cal-title">📅 릴리즈 캘린더</h2>
        <p class="cal-desc">전체 WBS 프로젝트의 마감일과 태스크 일정을 한눈에 확인하세요</p>
      </div>
      <div class="cal-controls">
        <div class="legend-row">
          <span class="legend-dot" style="background:var(--green)"></span><span class="legend-lbl">완료</span>
          <span class="legend-dot" style="background:var(--blue)"></span><span class="legend-lbl">진행중</span>
          <span class="legend-dot" style="background:var(--yellow)"></span><span class="legend-lbl">리스크</span>
          <span class="legend-dot" style="background:var(--red)"></span><span class="legend-lbl">지연</span>
          <span class="legend-dot" style="background:var(--muted)"></span><span class="legend-lbl">대기</span>
        </div>
        <div class="nav-row">
          <button class="nav-btn" @click="prevMonth">&#8249;</button>
          <span class="month-label">{{ year }}년 {{ month + 1 }}월</span>
          <button class="nav-btn" @click="nextMonth">&#8250;</button>
          <button class="today-btn" @click="goToday">오늘</button>
        </div>
      </div>
    </div>

    <div v-if="loading" class="loading-wrap">
      <div class="loading-spinner"></div>
      <span class="loading-text">프로젝트 불러오는 중...</span>
    </div>

    <div v-else class="cal-body">
      <!-- 사이드 패널 -->
      <div class="side-panel">
        <div class="side-title">이번 달 일정</div>
        <div v-if="monthEventsSorted.length === 0" class="side-empty">이번 달 일정이 없습니다</div>
        <div v-for="ev in monthEventsSorted" :key="ev.key" class="side-event"
          :class="'ev-' + ev.status"
          @click="selectedEvent = ev">
          <div class="side-ev-date">{{ fmtDay(ev.date) }}</div>
          <div class="side-ev-info">
            <div class="side-ev-name">{{ ev.label }}</div>
            <div class="side-ev-proj">{{ ev.project }}</div>
          </div>
          <span class="side-ev-badge" :class="'badge-' + ev.status">{{ STATUS_LABEL[ev.status] }}</span>
        </div>

        <div class="summary-cards">
          <div class="sum-card">
            <div class="sum-num" style="color:var(--text)">{{ allProjects.length }}</div>
            <div class="sum-label">전체 프로젝트</div>
          </div>
          <div class="sum-card">
            <div class="sum-num" style="color:var(--red)">{{ overdueProjects }}</div>
            <div class="sum-label">지연 프로젝트</div>
          </div>
          <div class="sum-card">
            <div class="sum-num" style="color:var(--yellow)">{{ riskProjects }}</div>
            <div class="sum-label">리스크 (D-14)</div>
          </div>
          <div class="sum-card">
            <div class="sum-num" style="color:var(--green)">{{ doneProjects }}</div>
            <div class="sum-label">완료</div>
          </div>
        </div>

        <div class="upcoming-title">⏰ 다가오는 마감 (30일 이내)</div>
        <div v-if="upcoming.length === 0" class="side-empty">30일 이내 마감 없음</div>
        <div v-for="p in upcoming" :key="'up-'+p.id" class="upcoming-row">
          <div class="upcoming-name">{{ p.name }}</div>
          <div class="upcoming-meta">
            <span class="upcoming-pm" v-if="p.pm">{{ p.pm }}</span>
            <span class="upcoming-date"
              :class="p.daysLeft < 0 ? 'overdue-text' : p.daysLeft <= 7 ? 'soon-text' : ''">
              {{ p.daysLeft < 0 ? Math.abs(p.daysLeft) + '일 지연' : p.daysLeft === 0 ? 'D-day' : 'D-' + p.daysLeft }}
            </span>
          </div>
        </div>
      </div>

      <!-- 캘린더 그리드 -->
      <div class="cal-grid-wrap">
        <div class="weekday-row">
          <div v-for="d in WEEKDAYS" :key="d" class="weekday-cell"
            :class="d === '일' ? 'sunday' : d === '토' ? 'saturday' : ''">{{ d }}</div>
        </div>
        <div class="cal-grid">
          <div v-for="(cell, idx) in cells" :key="idx"
            class="cal-cell"
            :class="{
              'other-month': !cell.thisMonth,
              'today-cell': cell.isToday,
              'sunday-cell': cell.weekday === 0,
              'saturday-cell': cell.weekday === 6
            }">
            <div class="cell-num" :class="cell.isToday ? 'today-num' : ''">{{ cell.day }}</div>
            <div class="cell-events">
              <div v-for="ev in cell.events.slice(0, 3)" :key="ev.key"
                class="cell-ev" :class="'cev-' + ev.status"
                :title="ev.label + ' — ' + ev.project"
                @click="selectedEvent = ev">
                <span class="cev-dot"></span>
                <span class="cev-text">{{ ev.label }}</span>
              </div>
              <div v-if="cell.events.length > 3" class="cell-more">+{{ cell.events.length - 3 }}개 더</div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 이벤트 상세 팝업 -->
    <div v-if="selectedEvent" class="ev-overlay" @click.self="selectedEvent = null">
      <div class="ev-popup">
        <div class="ev-popup-header" :class="'ev-header-' + selectedEvent.status">
          <div>
            <div class="ev-popup-type">{{ selectedEvent.type === 'project' ? '📁 프로젝트 마감' : '📌 태스크 마감' }}</div>
            <div class="ev-popup-name">{{ selectedEvent.label }}</div>
          </div>
          <button class="ev-close" @click="selectedEvent = null">✕</button>
        </div>
        <div class="ev-popup-body">
          <div class="ev-row"><span class="ev-key">프로젝트</span><span>{{ selectedEvent.project }}</span></div>
          <div class="ev-row" v-if="selectedEvent.pm"><span class="ev-key">담당 PM</span><span>{{ selectedEvent.pm }}</span></div>
          <div class="ev-row" v-if="selectedEvent.assignee"><span class="ev-key">담당자</span><span>{{ selectedEvent.assignee }}</span></div>
          <div class="ev-row"><span class="ev-key">마감일</span><span>{{ selectedEvent.date }}</span></div>
          <div class="ev-row">
            <span class="ev-key">상태</span>
            <span class="ev-badge" :class="'badge-' + selectedEvent.status">{{ STATUS_LABEL[selectedEvent.status] }}</span>
          </div>
          <div class="ev-row" v-if="selectedEvent.progress !== undefined">
            <span class="ev-key">진행률</span>
            <span>{{ selectedEvent.progress }}%</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { api } from '../api/index.js'
import { getStatus } from '../utils.js'

const WEEKDAYS = ['일', '월', '화', '수', '목', '금', '토']
const STATUS_LABEL = { done: '완료', progress: '진행중', risk: '리스크', overdue: '지연', pending: '대기' }

function diffDaysFromToday(dateStr) {
  if (!dateStr) return null
  const today = new Date(); today.setHours(0, 0, 0, 0)
  const d = new Date(dateStr); d.setHours(0, 0, 0, 0)
  return Math.round((d - today) / 86400000)
}

function projectStatus(proj) {
  if ((proj.progress || 0) >= 100) return 'done'
  if (!proj.endDate) return proj.status || 'pending'
  const diff = diffDaysFromToday(proj.endDate)
  if (diff < 0) return 'overdue'
  if (diff <= 14) return 'risk'
  if ((proj.progress || 0) > 0) return 'progress'
  return proj.status || 'pending'
}

export default {
  name: 'ReleaseCalendar',
  data() {
    const now = new Date()
    return {
      year: now.getFullYear(),
      month: now.getMonth(),
      today: new Date(),
      WEEKDAYS,
      STATUS_LABEL,
      loading: true,
      allProjects: [],
      allTasks: [],
      selectedEvent: null,
    }
  },
  async mounted() {
    await this.loadData()
  },
  computed: {
    cells() {
      const y = this.year, m = this.month
      const firstDay = new Date(y, m, 1).getDay()
      const lastDate = new Date(y, m + 1, 0).getDate()
      const prevLastDate = new Date(y, m, 0).getDate()
      const cells = []
      const todayStr = this.toDateStr(this.today)

      for (let i = firstDay - 1; i >= 0; i--) {
        const d = prevLastDate - i
        const date = new Date(y, m - 1, d)
        cells.push({ day: d, thisMonth: false, isToday: false, weekday: date.getDay(), events: [], dateStr: this.toDateStr(date) })
      }
      for (let d = 1; d <= lastDate; d++) {
        const date = new Date(y, m, d)
        const dateStr = this.toDateStr(date)
        cells.push({ day: d, thisMonth: true, isToday: dateStr === todayStr, weekday: date.getDay(), dateStr, events: this.eventsOnDate(dateStr) })
      }
      const remaining = 42 - cells.length
      for (let d = 1; d <= remaining; d++) {
        const date = new Date(y, m + 1, d)
        cells.push({ day: d, thisMonth: false, isToday: false, weekday: date.getDay(), events: [], dateStr: this.toDateStr(date) })
      }
      return cells
    },
    events() {
      const evs = []
      this.allProjects.forEach(p => {
        if (p.endDate) {
          evs.push({ key: 'proj-' + p.id, type: 'project', date: p.endDate, label: p.name, project: p.name, pm: p.pm, assignee: null, status: projectStatus(p), progress: p.progress })
        }
      })
      this.allTasks.forEach(t => {
        if (t.endDate) {
          evs.push({ key: 'task-' + t.id + '-' + t.projectId, type: 'task', date: t.endDate, label: t.task, project: t.projectName, pm: t.pm, assignee: t.assignee, status: getStatus(t), progress: t.progress })
        }
      })
      return evs
    },
    monthEventsSorted() {
      return this.events.filter(ev => {
        if (!ev.date) return false
        const [y, m] = ev.date.split('-').map(Number)
        return y === this.year && m - 1 === this.month
      }).sort((a, b) => a.date < b.date ? -1 : 1)
    },
    overdueProjects() { return this.allProjects.filter(p => projectStatus(p) === 'overdue').length },
    riskProjects()    { return this.allProjects.filter(p => projectStatus(p) === 'risk').length },
    doneProjects()    { return this.allProjects.filter(p => projectStatus(p) === 'done').length },
    upcoming() {
      return this.allProjects
        .filter(p => p.endDate)
        .map(p => ({ ...p, status: projectStatus(p), daysLeft: diffDaysFromToday(p.endDate) }))
        .filter(p => p.daysLeft !== null && p.daysLeft <= 30)
        .sort((a, b) => a.daysLeft - b.daysLeft)
    },
  },
  methods: {
    async loadData() {
      this.loading = true
      try {
        this.allProjects = await api.getProjects()
        const taskArrays = await Promise.all(
          this.allProjects.map(p =>
            api.getTasks(p.id)
              .then(tasks => tasks.map(t => ({ ...t, projectId: p.id, projectName: p.name, pm: p.pm })))
              .catch(() => [])
          )
        )
        this.allTasks = taskArrays.flat()
      } catch (e) {
        console.error(e)
      }
      this.loading = false
    },
    eventsOnDate(dateStr) { return this.events.filter(ev => ev.date === dateStr) },
    toDateStr(d) {
      const y = d.getFullYear()
      const m = String(d.getMonth() + 1).padStart(2, '0')
      const day = String(d.getDate()).padStart(2, '0')
      return `${y}-${m}-${day}`
    },
    fmtDay(dateStr) {
      if (!dateStr) return ''
      const [, m, d] = dateStr.split('-')
      return `${parseInt(m)}월 ${parseInt(d)}일`
    },
    prevMonth() { if (this.month === 0) { this.year--; this.month = 11 } else this.month-- },
    nextMonth() { if (this.month === 11) { this.year++; this.month = 0 } else this.month++ },
    goToday()   { const now = new Date(); this.year = now.getFullYear(); this.month = now.getMonth() },
  }
}
</script>

<style scoped>
.cal-page { padding: 24px; max-width: 1400px; margin: 0 auto }
.cal-topbar { display: flex; align-items: flex-start; justify-content: space-between; gap: 20px; margin-bottom: 24px; flex-wrap: wrap }
.cal-title { font-size: 20px; font-weight: 700; color: var(--text); margin-bottom: 4px }
.cal-desc  { font-size: 13px; color: var(--muted) }
.cal-controls { display: flex; flex-direction: column; align-items: flex-end; gap: 10px }
.legend-row { display: flex; align-items: center; gap: 10px }
.legend-dot { width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0 }
.legend-lbl { font-size: 12px; color: var(--muted) }
.nav-row { display: flex; align-items: center; gap: 8px }
.nav-btn { background: var(--bg2); border: 1px solid var(--border2); border-radius: 8px; color: var(--text); width: 32px; height: 32px; cursor: pointer; font-size: 18px; display: flex; align-items: center; justify-content: center; transition: all .15s; font-family: inherit }
.nav-btn:hover { background: var(--bg3) }
.month-label { font-size: 15px; font-weight: 700; color: var(--text); min-width: 110px; text-align: center }
.today-btn { background: var(--amber); color: #0a0800; border: none; border-radius: 8px; padding: 6px 14px; font-size: 13px; font-weight: 600; cursor: pointer; font-family: inherit; transition: all .15s }
.today-btn:hover { background: #f0b85a }

.loading-wrap { display: flex; align-items: center; justify-content: center; gap: 12px; padding: 60px; color: var(--muted) }
.loading-spinner { width: 24px; height: 24px; border: 2px solid var(--border2); border-top-color: var(--amber); border-radius: 50%; animation: spin 1s linear infinite }
.loading-text { font-size: 14px }
@keyframes spin { to { transform: rotate(360deg) } }

.cal-body { display: grid; grid-template-columns: 280px 1fr; gap: 20px; align-items: start }

.side-panel { background: var(--bg2); border: 1px solid var(--border); border-radius: 14px; overflow: hidden }
.side-title  { font-size: 13px; font-weight: 700; color: var(--muted); text-transform: uppercase; letter-spacing: .05em; padding: 16px 16px 10px; border-bottom: 1px solid var(--border) }
.side-empty  { font-size: 13px; color: var(--muted); padding: 20px 16px; text-align: center }
.side-event  { display: flex; align-items: center; gap: 10px; padding: 10px 16px; border-bottom: 1px solid var(--border); cursor: pointer; transition: background .15s }
.side-event:hover { background: var(--bg3) }
.side-ev-date { font-size: 11px; color: var(--muted); font-family: 'DM Mono', monospace; white-space: nowrap; min-width: 48px }
.side-ev-info { flex: 1; min-width: 0 }
.side-ev-name { font-size: 12px; font-weight: 600; color: var(--text); white-space: nowrap; overflow: hidden; text-overflow: ellipsis }
.side-ev-proj { font-size: 11px; color: var(--muted); white-space: nowrap; overflow: hidden; text-overflow: ellipsis }

.summary-cards { display: grid; grid-template-columns: 1fr 1fr; gap: 1px; border-top: 1px solid var(--border); border-bottom: 1px solid var(--border) }
.sum-card { padding: 14px 12px; text-align: center; background: var(--bg2) }
.sum-card:nth-child(odd) { border-right: 1px solid var(--border) }
.sum-card:nth-child(n+3) { border-top: 1px solid var(--border) }
.sum-num  { font-size: 22px; font-weight: 700; font-family: 'DM Mono', monospace }
.sum-label { font-size: 11px; color: var(--muted); margin-top: 2px }

.upcoming-title { font-size: 12px; font-weight: 700; color: var(--muted); text-transform: uppercase; letter-spacing: .04em; padding: 14px 16px 8px }
.upcoming-row   { display: flex; align-items: center; justify-content: space-between; padding: 8px 16px; gap: 8px; border-top: 1px solid var(--border) }
.upcoming-name  { font-size: 12px; font-weight: 600; color: var(--text); flex: 1; min-width: 0; overflow: hidden; text-overflow: ellipsis; white-space: nowrap }
.upcoming-meta  { display: flex; flex-direction: column; align-items: flex-end; gap: 2px; flex-shrink: 0 }
.upcoming-pm    { font-size: 10px; color: var(--muted) }
.upcoming-date  { font-size: 11px; font-family: 'DM Mono', monospace; font-weight: 700; color: var(--text) }
.overdue-text   { color: var(--red) !important }
.soon-text      { color: var(--yellow) !important }

.cal-grid-wrap { background: var(--bg2); border: 1px solid var(--border); border-radius: 14px; overflow: hidden }
.weekday-row   { display: grid; grid-template-columns: repeat(7, 1fr); border-bottom: 1px solid var(--border) }
.weekday-cell  { text-align: center; padding: 10px 4px; font-size: 11px; font-weight: 700; color: var(--muted); text-transform: uppercase; letter-spacing: .06em }
.weekday-cell.sunday   { color: var(--red) }
.weekday-cell.saturday { color: var(--blue) }

.cal-grid { display: grid; grid-template-columns: repeat(7, 1fr) }
.cal-cell { min-height: 110px; border-right: 1px solid var(--border); border-bottom: 1px solid var(--border); padding: 6px 5px; transition: background .15s }
.cal-cell:hover { background: var(--bg3) }
.cal-cell:nth-child(7n) { border-right: none }
.other-month { opacity: .35 }
.today-cell  { background: rgba(232,169,74,.07) }
.sunday-cell  .cell-num { color: var(--red) }
.saturday-cell .cell-num { color: var(--blue) }
.cell-num { font-size: 12px; font-weight: 600; color: var(--text); margin-bottom: 4px }
.today-num { background: var(--amber); color: #0a0800; width: 22px; height: 22px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 12px; font-weight: 700 }
.cell-events { display: flex; flex-direction: column; gap: 2px }
.cell-ev { display: flex; align-items: center; gap: 4px; padding: 2px 4px; border-radius: 4px; cursor: pointer; transition: opacity .15s }
.cell-ev:hover { opacity: .8 }
.cev-dot  { width: 6px; height: 6px; border-radius: 50%; flex-shrink: 0 }
.cev-text { font-size: 10px; font-weight: 600; white-space: nowrap; overflow: hidden; text-overflow: ellipsis }
.cell-more { font-size: 10px; color: var(--muted); padding-left: 4px }

.ev-done     { border-left: 3px solid var(--green) }
.ev-progress { border-left: 3px solid var(--blue) }
.ev-risk     { border-left: 3px solid var(--yellow) }
.ev-overdue  { border-left: 3px solid var(--red) }
.ev-pending  { border-left: 3px solid var(--muted) }

.cev-done     { background: var(--green-dim) }.cev-done .cev-dot { background: var(--green) }.cev-done .cev-text { color: var(--green) }
.cev-progress { background: var(--blue-dim) }.cev-progress .cev-dot { background: var(--blue) }.cev-progress .cev-text { color: var(--blue) }
.cev-risk     { background: var(--yellow-dim) }.cev-risk .cev-dot { background: var(--yellow) }.cev-risk .cev-text { color: var(--yellow) }
.cev-overdue  { background: var(--red-dim) }.cev-overdue .cev-dot { background: var(--red) }.cev-overdue .cev-text { color: var(--red) }
.cev-pending  { background: var(--bg4) }.cev-pending .cev-dot { background: var(--muted) }.cev-pending .cev-text { color: var(--muted) }

.badge-done    { background: var(--green-dim); color: var(--green); padding: 2px 6px; border-radius: 5px; font-size: 11px; font-weight: 600 }
.badge-progress{ background: var(--blue-dim);  color: var(--blue);  padding: 2px 6px; border-radius: 5px; font-size: 11px; font-weight: 600 }
.badge-risk    { background: var(--yellow-dim); color: var(--yellow); padding: 2px 6px; border-radius: 5px; font-size: 11px; font-weight: 600 }
.badge-overdue { background: var(--red-dim);   color: var(--red);   padding: 2px 6px; border-radius: 5px; font-size: 11px; font-weight: 600 }
.badge-pending { background: var(--bg4);       color: var(--muted); padding: 2px 6px; border-radius: 5px; font-size: 11px; font-weight: 600 }

.ev-overlay { position: fixed; inset: 0; background: rgba(0,0,0,.45); z-index: 500; display: flex; align-items: center; justify-content: center }
.ev-popup   { background: var(--bg2); border: 1px solid var(--border2); border-radius: 14px; width: 400px; max-width: 90vw; overflow: hidden }
.ev-popup-header { display: flex; align-items: flex-start; justify-content: space-between; padding: 18px 20px; gap: 12px }
.ev-header-done     { border-left: 4px solid var(--green) }
.ev-header-progress { border-left: 4px solid var(--blue) }
.ev-header-risk     { border-left: 4px solid var(--yellow) }
.ev-header-overdue  { border-left: 4px solid var(--red) }
.ev-header-pending  { border-left: 4px solid var(--muted) }
.ev-popup-type { font-size: 11px; color: var(--muted); margin-bottom: 4px }
.ev-popup-name { font-size: 15px; font-weight: 700; color: var(--text) }
.ev-close { background: none; border: none; color: var(--muted); cursor: pointer; font-size: 16px; flex-shrink: 0 }
.ev-close:hover { color: var(--text) }
.ev-popup-body { padding: 16px 20px 20px; display: flex; flex-direction: column; gap: 10px; border-top: 1px solid var(--border) }
.ev-row { display: flex; align-items: center; gap: 12px; font-size: 13px }
.ev-key { color: var(--muted); font-size: 12px; width: 52px; flex-shrink: 0 }
</style>
