<template>
  <div class="list-page">
    <div class="list-card">
      <!-- 헤더 -->
      <div class="list-header">
        <div class="search-wrap">
          <svg class="search-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/></svg>
          <input v-model="search" class="search-input" placeholder="프로젝트명, 담당자로 검색..." />
          <button v-if="search" class="clear-btn" @click="search=''">✕</button>
        </div>
        <div class="header-right">
          <!-- 다중 선택 삭제 -->
          <template v-if="selected.length > 0">
            <span class="sel-count">{{ selected.length }}개 선택됨</span>
            <button class="btn btn-danger-ghost btn-sm" @click="deleteSelected">🗑 선택 삭제</button>
            <button class="btn btn-ghost btn-sm" @click="selected=[]">취소</button>
          </template>
          <template v-else>
            <span class="count-label">{{ sorted.length }}개 항목</span>
            <select v-model="sortKey" class="filter-select">
              <option value="latest">최신 등록순</option>
              <option value="oldest">오래된순</option>
              <option value="endDate">마감일 빠른순</option>
              <option value="name">이름순</option>
            </select>
            <select v-model="statusFilter" class="filter-select">
              <option value="">전체 상태</option>
              <option value="progress">진행중</option>
              <option value="risk">리스크</option>
              <option value="overdue">지연</option>
              <option value="done">완료</option>
              <option value="pending">대기</option>
            </select>
          </template>
        </div>
      </div>

      <!-- 컬럼 헤더 -->
      <div class="col-header">
        <div class="col-check">
          <input type="checkbox" :checked="allSelected" @change="toggleAll" />
        </div>
        <span style="flex:2">프로젝트명</span>
        <span style="width:100px;text-align:center">담당 PM</span>
        <span style="width:90px;text-align:center">상태</span>
        <span style="width:140px;text-align:center">진행률</span>
        <span style="width:96px;text-align:center">마감일</span>
        <span style="width:72px;text-align:center">등록일</span>
        <span style="width:52px;text-align:center">태스크</span>
        <span style="width:50px"></span>
      </div>

      <!-- 로딩 스켈레톤 -->
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

      <div v-for="proj in paged" :key="proj.id" class="proj-row"
        :class="{ selected: selected.includes(proj.id) }"
        @click="handleRowClick(proj, $event)">
        <!-- 체크박스 -->
        <div class="col-check" @click.stop>
          <input type="checkbox" :value="proj.id" v-model="selected" />
        </div>
        <!-- 프로젝트명 -->
        <div class="proj-name-cell" style="flex:2">
          <div class="proj-name">{{ proj.name }}</div>
          <div class="proj-desc">{{ proj.description || '설명 없음' }}</div>
        </div>
        <!-- 담당 PM -->
        <div class="proj-pm" style="width:100px;text-align:center;word-break:break-word;white-space:normal">{{ proj.pm || '-' }}</div>
        <!-- 상태 -->
        <div style="width:90px;display:flex;justify-content:center">
          <span class="status-badge" :class="STATUS_CLASS[proj.status || 'pending']">
            {{ STATUS_LABEL[proj.status || 'pending'] }}
          </span>
        </div>
        <!-- 진행률 -->
        <div style="width:140px;display:flex;justify-content:center">
          <div class="prog-row">
            <div class="prog-wrap">
              <div class="prog-fill" :style="{ width:(proj.progress||0)+'%', background: progColor(proj.progress||0) }"></div>
            </div>
            <span class="prog-text">{{ proj.progress || 0 }}%</span>
          </div>
        </div>
        <!-- 마감일 -->
        <div class="proj-date" style="width:96px;text-align:center">{{ proj.endDate || '-' }}</div>
        <!-- 등록일 -->
        <div class="proj-date" style="width:72px;text-align:center;font-size:11px">{{ fmtDate(proj.createdAt) }}</div>
        <!-- 태스크 수 -->
        <div class="proj-count" style="width:52px;text-align:center">{{ proj.total || 0 }}</div>
        <!-- 3dot -->
        <div class="action-cell" style="width:50px" @click.stop>
          <div class="menu-wrapper">
            <button class="icon-btn dot-btn" @click="toggleMenu(proj.id, $event)">
              <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="1"/><circle cx="12" cy="5" r="1"/><circle cx="12" cy="19" r="1"/></svg>
            </button>
            <div v-if="activeMenuId===proj.id" class="dropdown-menu">
              <button class="dropdown-item" @click="handleEdit(proj)">수정</button>
              <button class="dropdown-item danger" @click="handleDelete(proj)">삭제</button>
            </div>
          </div>
        </div>
      </div>

      <!-- 페이지네이션 -->
      <div class="pagination" v-if="totalPages > 1">
        <span class="pg-info">{{ (page-1)*PAGE_SIZE+1 }}-{{ Math.min(page*PAGE_SIZE, sorted.length) }} / {{ sorted.length }}</span>
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

const PAGE_SIZE = 10

export default {
  name: 'WBSList',
  props: { projects: Array, loading: { type: Boolean, default: false } },
  emits: ['select', 'new', 'edit', 'delete'],
  data() {
    return {
      search: '', statusFilter: '', sortKey: 'latest',
      page: 1, PAGE_SIZE,
      STATUS_LABEL, STATUS_CLASS,
      activeMenuId: null,
      selected: [],
    }
  },
  computed: {
    filtered() {
      const q = this.search.toLowerCase()
      return this.projects.filter(p => {
        const matchSearch = !q || p.name.toLowerCase().includes(q) || (p.pm||'').toLowerCase().includes(q)
        const matchStatus = !this.statusFilter || p.status === this.statusFilter
        return matchSearch && matchStatus
      })
    },
    sorted() {
      const list = [...this.filtered]
      if (this.sortKey === 'latest')  list.sort((a,b) => (b.createdAt||'') > (a.createdAt||'') ? 1 : -1)
      if (this.sortKey === 'oldest')  list.sort((a,b) => (a.createdAt||'') > (b.createdAt||'') ? 1 : -1)
      if (this.sortKey === 'endDate') list.sort((a,b) => (a.endDate||'9999') > (b.endDate||'9999') ? 1 : -1)
      if (this.sortKey === 'name')    list.sort((a,b) => a.name.localeCompare(b.name))
      return list
    },
    totalPages() { return Math.ceil(this.sorted.length / PAGE_SIZE) || 1 },
    paged()      { const s=(this.page-1)*PAGE_SIZE; return this.sorted.slice(s, s+PAGE_SIZE) },
    allSelected(){ return this.paged.length > 0 && this.paged.every(p => this.selected.includes(p.id)) },
  },
  watch: {
    search()      { this.page = 1 },
    statusFilter(){ this.page = 1 },
    sortKey()     { this.page = 1 },
  },
  mounted()      { document.addEventListener('click', this.closeMenu) },
  beforeUnmount(){ document.removeEventListener('click', this.closeMenu) },
  methods: {
    fmtDate(d) {
      if (!d) return '-'
      return String(d).slice(0, 10)
    },
    progColor(p) {
      if (p >= 100) return 'var(--green)'
      if (p >= 70)  return '#4ade80'
      if (p >= 40)  return 'var(--yellow)'
      if (p > 0)    return '#fb923c'
      return 'var(--muted)'
    },
    handleRowClick(proj, e) {
      if (this.selected.length > 0) {
        const idx = this.selected.indexOf(proj.id)
        if (idx >= 0) this.selected.splice(idx, 1)
        else this.selected.push(proj.id)
      } else {
        this.$emit('select', proj)
      }
    },
    toggleAll(e) {
      if (e.target.checked) this.selected = this.paged.map(p => p.id)
      else this.selected = []
    },
    async deleteSelected() {
      if (!confirm(this.selected.length + '개 WBS를 삭제하시겠습니까?\n포함된 태스크도 모두 삭제됩니다.')) return
      for (const id of [...this.selected]) {
        this.$emit('delete', id)
      }
      this.selected = []
    },
    toggleMenu(id, e) {
      this.activeMenuId = (this.activeMenuId === id) ? null : id
      if (this.activeMenuId) {
        this.$nextTick(() => {
          const menu = document.querySelector('.dropdown-menu')
          if (menu && e) {
            const rect = e.currentTarget.getBoundingClientRect()
            menu.style.top = (rect.bottom + 4) + 'px'
            menu.style.left = (rect.right - 88) + 'px'
          }
        })
      }
    },
    closeMenu(e) {
      if (!e.target.closest('.menu-wrapper')) this.activeMenuId = null
    },
    handleEdit(proj)  { this.$emit('edit', proj); this.closeMenu() },
    handleDelete(proj){
      if (!confirm('[' + proj.name + ']\n이 WBS를 삭제하시겠습니까?')) return
      this.$emit('delete', proj.id); this.closeMenu()
    },
  }
}
</script>

<style scoped>
.list-page { padding:24px }
.list-card { background:var(--bg2); border:1px solid var(--border); border-radius:14px; overflow:hidden }

.list-header { display:flex; align-items:center; justify-content:space-between; gap:12px; padding:16px 20px; border-bottom:1px solid var(--border); flex-wrap:wrap }
.search-wrap { display:flex; align-items:center; gap:8px; background:var(--bg3); border:1px solid var(--border2); border-radius:10px; padding:10px 16px; flex:1; min-width:200px }
.search-icon { width:16px; height:16px; color:var(--muted); flex-shrink:0 }
.search-input{ background:transparent; border:none; outline:none; color:var(--text); font-size:14px; width:100%; font-family:inherit }
.search-input::placeholder{ color:var(--muted) }
.clear-btn   { background:none; border:none; color:var(--muted); cursor:pointer; font-size:14px }
.header-right{ display:flex; align-items:center; gap:8px; flex-wrap:wrap }
.count-label { font-size:13px; color:var(--muted) }
.sel-count   { font-size:13px; font-weight:600; color:var(--amber) }
.filter-select{ background:var(--bg2); border:1px solid var(--border2); border-radius:8px; padding:7px 10px; color:var(--text); font-size:13px; outline:none; cursor:pointer }

/* 체크박스 열 */
.col-check { width:40px; flex-shrink:0; display:flex; align-items:center; justify-content:center }
.col-check input { cursor:pointer; width:15px; height:15px; accent-color:var(--amber) }

.col-header { display:flex; align-items:center; padding:12px 20px; background:var(--bg3); border-bottom:1px solid var(--border) }
.col-header span { font-size:12px; color:var(--muted); font-weight:600; text-transform:uppercase; letter-spacing:.04em }

.proj-row { display:flex; align-items:center; padding:16px 20px; border-bottom:1px solid var(--border); cursor:pointer; transition:background .15s }
.proj-row:hover { background:var(--bg3) }
.proj-row.selected { background:var(--amber-dim) }
.proj-row:last-child { border-bottom:none }

.proj-name-cell { overflow:hidden }
.proj-name  { font-size:14px; font-weight:600; color:var(--text); white-space:nowrap; overflow:hidden; text-overflow:ellipsis }
.proj-desc  { font-size:12px; color:var(--muted); margin-top:2px; white-space:nowrap; overflow:hidden; text-overflow:ellipsis }
.proj-pm, .proj-date, .proj-count { font-size:13px; color:var(--text) }
.status-badge { padding:4px 10px; border-radius:7px; font-size:12px; font-weight:600 }
.sb-done    { background:var(--green-dim); color:var(--green) }
.sb-progress{ background:var(--blue-dim);  color:var(--blue) }
.sb-risk    { background:var(--yellow-dim);color:var(--yellow) }
.sb-overdue { background:var(--red-dim);   color:var(--red) }
.sb-pending { background:var(--bg4);       color:var(--muted) }

.prog-row  { display:flex; align-items:center; justify-content:flex-start; gap:6px }
.prog-wrap { width:70px; flex-shrink:0; height:6px; background:var(--bg4); border-radius:3px; overflow:hidden }
.prog-fill { height:100%; transition:width .3s }
.prog-text { font-size:12px; font-family:'DM Mono',monospace; color:var(--muted) }

.action-cell  { text-align:center }
.menu-wrapper { position:relative; display:inline-block }
.dot-btn      { background:none; border:none; color:var(--muted); cursor:pointer; padding:4px; border-radius:5px; display:flex; align-items:center }
.dot-btn:hover{ background:var(--bg4); color:var(--text) }
.dropdown-menu{ position:fixed; background:var(--bg2); border:1px solid var(--border2); border-radius:8px; padding:4px; z-index:999; min-width:88px; box-shadow:0 2px 8px rgba(0,0,0,.15); display:flex; flex-direction:column; gap:2px }
.dropdown-item{ width:100%; background:none; border:none; padding:7px 10px; text-align:left; color:var(--text); font-size:13px; cursor:pointer; border-radius:5px; font-weight:500; font-family:inherit }
.dropdown-item:hover { background:var(--bg3) }
.dropdown-item.danger { color:var(--red) }

.btn { display:inline-flex; align-items:center; padding:6px 12px; border-radius:7px; font-size:12px; cursor:pointer; border:none; font-family:inherit; font-weight:500 }
.btn-ghost { background:transparent; color:var(--muted); border:1px solid var(--border2) }.btn-ghost:hover{ background:var(--bg3) }
.btn-danger-ghost { background:transparent; color:var(--red); border:1px solid var(--red-dim) }.btn-danger-ghost:hover{ background:var(--red-dim) }
.btn-sm { padding:5px 10px; font-size:12px }
.icon-btn{ background:none; border:none; cursor:pointer; display:flex; align-items:center }

.pagination { display:flex; align-items:center; justify-content:space-between; padding:14px 20px; border-top:1px solid var(--border) }
.pg-info { font-size:12px; color:var(--muted) }
.pg-btns { display:flex; gap:4px }
.pg-btn  { padding:5px 10px; border-radius:6px; border:1px solid var(--border2); background:transparent; color:var(--muted); font-size:12px; cursor:pointer; font-family:inherit }
.pg-btn:disabled { opacity:.4; cursor:default }
.pg-btn.on { background:var(--bg4); color:var(--text) }

.skeleton-wrap { padding:8px 0 }
.skeleton-row  { display:flex; align-items:center; gap:12px; padding:14px 20px; border-bottom:1px solid var(--border) }
.skeleton-row:last-child { border-bottom:none }
.sk { background:var(--bg4); border-radius:6px; animation:shimmer 1.4s infinite }
.sk-name { flex:2; height:14px }
.sk-sm   { width:80px; height:12px }
.sk-md   { width:120px; height:12px }
.sk-xs   { width:40px; height:12px }
@keyframes shimmer { 0%{opacity:.4} 50%{opacity:.9} 100%{opacity:.4} }

.empty-state { text-align:center; padding:80px 20px; color:var(--muted); font-size:15px; font-weight:500 }
</style>