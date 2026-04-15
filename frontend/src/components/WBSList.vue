<template>
  <div class="list-page">
    <div class="list-card">
      <div class="list-header">
        <div class="search-wrap">
          <svg class="search-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/></svg>
          <input v-model="search" class="search-input" placeholder="프로젝트명, 담당자로 검색..." />
          <button v-if="search" class="clear-btn" @click="search=''">✕</button>
        </div>
        <div class="header-right">
          <span class="count-label">{{ filtered.length }}개 항목</span>
          <select v-model="statusFilter" class="filter-select">
            <option value="">전체 상태</option>
            <option value="progress">진행중</option>
            <option value="risk">리스크</option>
            <option value="overdue">지연</option>
            <option value="done">완료</option>
            <option value="pending">대기</option>
          </select>
        </div>
      </div>

      <div class="col-header">
        <span style="flex:2">프로젝트명</span>
        <span style="width:120px;text-align:center">담당 PM</span>
        <span style="width:100px;text-align:center">상태</span>
        <span style="width:150px;text-align:center">진행률</span>
        <span style="width:100px;text-align:center">마감일</span>
        <span style="width:60px;text-align:center">태스크</span>
        <span style="width:60px"></span>
      </div>

      <div v-if="loading" class="skeleton-wrap">
        <div v-for="i in 4" :key="i" class="skeleton-row">
          <div class="sk sk-name"></div>
          <div class="sk sk-sm"></div>
          <div class="sk sk-sm"></div>
          <div class="sk sk-md"></div>
          <div class="sk sk-sm"></div>
          <div class="sk sk-xs"></div>
        </div>
      </div>

      <div v-else-if="paged.length === 0" class="empty-state">
        <div>{{ search || statusFilter ? '검색 결과가 없습니다' : 'WBS 프로젝트가 없습니다' }}</div>
      </div>

      <div v-for="proj in paged" :key="proj.id" class="proj-row" @click="$emit('select', proj)">
        <div class="proj-name-cell" style="flex:2">
          <div class="proj-name">{{ proj.name.slice(0,200) }}</div>
          <div class="proj-desc">{{ proj.description || '설명 없음' }}</div>
        </div>
        <div class="proj-pm" style="width:120px;text-align:center;word-break:break-word;white-space:normal">{{ proj.pm || '-' }}</div>
        <div style="width:100px;display:flex;justify-content:center">
          <span class="status-badge" :class="STATUS_CLASS[proj.status || 'pending']">
            {{ STATUS_LABEL[proj.status || 'pending'] }}
          </span>
        </div>
        <div style="width:150px;display:flex;justify-content:center">
          <div class="prog-row">
            <div class="prog-wrap">
              <div class="prog-fill" :style="{ width:(proj.progress||0)+'%', background: progColor(proj.progress||0) }"></div>
            </div>
            <span class="prog-text">{{ proj.progress || 0 }}%</span>
          </div>
        </div>
        <div class="proj-date" style="width:100px;text-align:center">{{ proj.endDate || '-' }}</div>
        <div class="proj-count" style="width:60px;text-align:center">{{ proj.total || 0 }}</div>
        
        <div class="action-cell" style="width:60px">
          <div class="menu-wrapper" @click.stop>
            <button class="icon-btn dot-btn" @click="toggleMenu(proj.id)">
              <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="1"/><circle cx="12" cy="5" r="1"/><circle cx="12" cy="19" r="1"/></svg>
            </button>
            <div v-if="activeMenuId === proj.id" class="dropdown-menu">
              <button class="dropdown-item" @click="handleEdit(proj)">수정</button>
              <button class="dropdown-item danger" @click="handleDelete(proj)">삭제</button>
            </div>
          </div>
        </div>
      </div>

      <div class="pagination" v-if="totalPages > 1">
        <span class="pg-info">{{ (page-1)*PAGE_SIZE+1 }}-{{ Math.min(page*PAGE_SIZE, filtered.length) }} / {{ filtered.length }}</span>
        <div class="pg-btns">
          <button class="pg-btn" :disabled="page===1" @click="page--">이전</button>
          <button v-for="n in totalPages" :key="n" class="pg-btn" :class="{on: page===n}" @click="page=n">{{ n }}</button>
          <button class="pg-btn" :disabled="page===totalPages" @click="page++">다음</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { STATUS_LABEL, STATUS_CLASS } from '../utils.js'
const PAGE_SIZE = 15

export default {
  name: 'WBSList',
  props: { projects: Array, loading: { type: Boolean, default: false } },
  emits: ['select', 'new', 'edit', 'delete'],
  data() {
    return { search: '', statusFilter: '', page: 1, PAGE_SIZE, STATUS_LABEL, STATUS_CLASS, activeMenuId: null }
  },
  computed: {
    filtered() {
      const q = this.search.toLowerCase()
      return this.projects.filter(p => {
        if (this.statusFilter && p.status !== this.statusFilter) return false
        if (q && !p.name.toLowerCase().includes(q) && !(p.pm||'').toLowerCase().includes(q)) return false
        return true
      })
    },
    totalPages() { return Math.ceil(this.filtered.length / PAGE_SIZE) || 1 },
    paged() {
      const s = (this.page - 1) * PAGE_SIZE
      return this.filtered.slice(s, s + PAGE_SIZE)
    }
  },
  mounted() { document.addEventListener('click', this.closeMenu) },
  beforeUnmount() { document.removeEventListener('click', this.closeMenu) },
  methods: {
    pbClass(s) { return { done:'pf-green', progress:'pf-blue', risk:'pf-yellow', overdue:'pf-red' }[s] || 'pf-blue' },
    progColor(p) {
      if (p >= 100) return 'var(--green)'
      if (p >= 70)  return '#4ade80'
      if (p >= 40)  return 'var(--yellow)'
      if (p > 0)    return '#fb923c'
      return 'var(--muted)'
    },
    toggleMenu(id) { this.activeMenuId = (this.activeMenuId === id) ? null : id },
    closeMenu() { this.activeMenuId = null },
    handleEdit(p) { this.$emit('edit', p); this.closeMenu() },
    handleDelete(p) { if(confirm(`[${p.name}] 프로젝트를 삭제하시겠습니까?`)) this.$emit('delete', p.id); this.closeMenu() }
  }
}
</script>

<style scoped>
.list-page { padding: 32px }
.list-card { background:var(--bg2); border:1px solid var(--border); border-radius:16px; box-shadow: 0 4px 20px rgba(0,0,0,0.1); position: relative; }
.list-header { border-top-left-radius: 16px; border-top-right-radius: 16px; display:flex; align-items:center; gap:12px; padding:16px 24px; border-bottom:1px solid var(--border); background:var(--bg3); flex-wrap:wrap }
.search-wrap { flex:1; min-width:200px; display:flex; align-items:center; gap:12px; background:var(--bg2); border:1px solid var(--border2); border-radius:10px; padding:10px 16px }
.search-icon { width:18px; height:18px; color:var(--muted); flex-shrink:0 }
.search-input { background:transparent; border:none; outline:none; color:var(--text); font-size:14px; flex:1; font-family:inherit }
.clear-btn { background:none; border:none; color:var(--muted); cursor:pointer; padding:0 4px; font-size:14px; flex-shrink:0 }
.header-right { display:flex; align-items:center; gap:10px; flex-shrink:0 }
.count-label  { font-size:13px; color:var(--muted); white-space:nowrap }
.filter-select { background:var(--bg2); border:1px solid var(--border2); border-radius:8px; padding:8px 12px; color:var(--text); font-size:13px; outline:none; cursor:pointer }

.col-header { display:flex; align-items:center; padding:16px 24px; background:var(--bg3); border-bottom:1px solid var(--border) }
.col-header span { font-size:15px; color:var(--muted); font-weight:700; text-transform:uppercase; letter-spacing:.05em }

.proj-row { display:flex; align-items:center; padding:20px 24px; border-bottom:1px solid var(--border); cursor:pointer; transition:background .2s }
.proj-row:hover { background:var(--bg3) }
.proj-name { font-size:18px; font-weight:700; color:var(--text) }
.proj-desc { font-size:14px; color:var(--muted); margin-top:6px }
.proj-pm, .proj-date, .proj-count { font-size:15px; color:var(--text) }

.status-badge { padding:6px 12px; border-radius:8px; font-size:13px; font-weight:700 }

/* 💡 WBS List 프로그레스 바 수정: 간격 4px, 볼드 해제 */
.prog-row { display: flex; align-items: center; justify-content: flex-start; gap: 4px; }
.prog-wrap { width: 80px; flex-shrink: 0; height: 8px; background: var(--bg4); border-radius: 4px; overflow: hidden; }
.prog-fill { height: 100%; transition: width 0.4s; }
.prog-text { font-size: 14px; font-weight: 400; font-family: 'DM Mono', monospace; color: var(--text); white-space: nowrap; }

.action-cell { position: relative; text-align: center; }
.menu-wrapper { position: relative; display: inline-block; }
.dot-btn { padding: 8px; border-radius: 8px; color: var(--muted); background:none; border:none; cursor:pointer; display:flex; align-items:center; justify-content:center; }
.dot-btn:hover { background: var(--bg4); color: var(--text); }

.dropdown-menu { position: absolute; right: 0; top: 40px; background: var(--bg2); border: 1px solid var(--border2); border-radius:10px; padding:8px; z-index:999; min-width:100px; box-shadow: 0 8px 24px rgba(0,0,0,0.5); display:flex; flex-direction:column; gap:2px; }
.dropdown-item { width:100%; background:none; border:none; padding:10px; text-align:left; color:var(--text); font-size:14px; cursor:pointer; border-radius:6px; font-weight:600; }
.dropdown-item:hover { background:var(--bg3) }
.dropdown-item.danger { color:var(--red) }
.dropdown-item.danger:hover { background:var(--red-dim) }

.pagination { border-bottom-left-radius: 16px; border-bottom-right-radius: 16px; display:flex; align-items:center; justify-content:space-between; padding:20px 24px; background:var(--bg3) }
.pg-info { font-size:14px; color:var(--muted) }
.pg-btn { padding:8px 16px; border-radius:8px; border:1px solid var(--border2); background:transparent; color:var(--text); font-size:14px; cursor:pointer; font-weight:600 }
.pg-btn.on { background:var(--amber); color:#000; border-color:var(--amber) }
.pg-btn:disabled { opacity:0.3; cursor:not-allowed }
.empty-state { text-align:center; padding:80px 20px; color:var(--muted); font-size:15px; font-weight:500; }

/* 스켈레톤 로딩 */
.skeleton-wrap { padding: 8px 0 }
.skeleton-row  { display:flex; align-items:center; gap:12px; padding:14px 20px; border-bottom:1px solid var(--border) }
.skeleton-row:last-child { border-bottom:none }
.sk { background:var(--bg4); border-radius:6px; animation: shimmer 1.4s infinite }
.sk-name { flex:2; height:14px }
.sk-sm   { width:80px; height:12px }
.sk-md   { width:120px; height:12px }
.sk-xs   { width:40px; height:12px }
@keyframes shimmer {
  0%   { opacity:.4 }
  50%  { opacity:.9 }
  100% { opacity:.4 }
}
</style>