<template>
  <div>
    <div class="detail-bar">
      <div class="breadcrumb">
        <span class="bc-link" @click="$emit('back')">WBS 목록</span>
        <span class="bc-sep">›</span>
        <span class="bc-cur">{{ project.name }}</span>
      </div>
      <div class="bar-right">
        <div class="inner-search">
          <span style="color:var(--muted);font-size:13px">⌕</span>
          <input v-model="taskSearch" placeholder="태스크, 담당자 검색..." />
        </div>

        <!-- 업로드 드롭다운 -->
        <div class="upload-wrap" ref="uploadWrap">
          <button class="btn btn-ghost btn-sm" @click="showUploadMenu=!showUploadMenu" :disabled="isUploading">
            {{ isUploading ? '⏳ 업로드 중...' : '업로드 ▾' }}
          </button>
          <div v-if="showUploadMenu" class="upload-menu">
            <input type="file" ref="excelInput" style="display:none" accept=".xlsx,.xls,.csv" @change="handleFileUpload" />
            <button class="upload-item" @click="$refs.excelInput.click(); showUploadMenu=false">
              📄 엑셀 파일 업로드
            </button>
            <button class="upload-item" @click="showSheetsModal=true; showUploadMenu=false">
              🔗 Google Sheets 링크
            </button>
            <div class="upload-divider"></div>
            <button class="upload-item" @click="downloadTemplate(); showUploadMenu=false">
              ⬇️ 업로드 양식 다운받기
            </button>
          </div>
        </div>

        <button class="btn btn-ghost btn-sm" @click="$emit('edit-project', project)">프로젝트 수정</button>
        <button class="btn btn-primary btn-sm" @click="openAdd">+ 태스크 추가</button>
      </div>
    </div>

    <div class="detail-body">
      <!-- 메트릭 -->
      <div class="metrics">
        <div class="mc"><div class="mc-label">전체</div><div class="mc-val" style="color:var(--blue)">{{ tasks.length }}</div></div>
        <div class="mc"><div class="mc-label">진행중</div><div class="mc-val" style="color:var(--green)">{{ cnt('progress') + cnt('done') }}</div></div>
        <div class="mc" :title="'마감일 7일 이내 미완료 태스크'">
          <div class="mc-label">리스크 <span class="mc-hint">D-7 이내</span></div>
          <div class="mc-val" style="color:var(--yellow)">{{ cnt('risk') }}</div>
        </div>
        <div class="mc mc-clickable" @click="focusOverdue" title="클릭하면 지연 태스크로 이동">
          <div class="mc-label">지연 <span class="mc-arrow">↓</span></div>
          <div class="mc-val" style="color:var(--red)">{{ cnt('overdue') }}</div>
          <div v-if="cnt('overdue')" class="mc-sub">클릭해서 확인</div>
        </div>
      </div>

      <!-- 탭 -->
      <div class="tabs">
        <div v-for="t in TABS" :key="t.key" class="tab" :class="{on: activeTab===t.key}" @click="activeTab=t.key">
          {{ t.label }}
        </div>
      </div>

      <task-table
        v-if="activeTab==='tasks'"
        :tasks="tasks"
        :search="taskSearch"
        :focus-overdue-at="focusOverdueAt"
        :loading="tasksLoading"
        @edit="openEdit"
        @delete="deleteTask"
      />
      <gantt-chart v-if="activeTab==='gantt'" :tasks="tasks" />
      <notif-panel v-if="activeTab==='notif'" :tasks="tasks" :logs="logs"
        @toast="$emit('toast',$event)" @reload-logs="$emit('reload-logs')" />
    </div>

    <!-- 태스크 폼 -->
    <task-form v-model="showForm" :edit-task="editingTask" :project-id="project.id"
      @save="saveTask" @delete="deleteTask" />

    <!-- Google Sheets 모달 -->
    <div v-if="showSheetsModal" class="overlay" @click.self="showSheetsModal=false">
      <div class="modal">
        <div class="modal-title">Google Sheets 링크로 업로드</div>
        <p class="modal-desc">
          Google Sheets를 <b>링크가 있는 모든 사용자 — 뷰어</b> 공유로 설정 후 URL을 붙여넣으세요.
        </p>
        <div class="field">
          <label>Google Sheets URL</label>
          <input v-model="sheetsUrl" placeholder="https://docs.google.com/spreadsheets/d/..." />
        </div>
        <div class="field">
          <label>시트 이름 (선택, 기본: 첫 번째 시트)</label>
          <input v-model="sheetsName" placeholder="Sheet1" />
        </div>
        <div class="modal-actions">
          <button class="btn btn-ghost" @click="showSheetsModal=false">취소</button>
          <button class="btn btn-primary" @click="handleSheetsUpload" :disabled="isUploading">
            {{ isUploading ? '가져오는 중...' : '가져오기' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { api } from '../api/index.js'
import { getStatus } from '../utils.js'
import TaskTable  from './TaskTable.vue'
import GanttChart from './GanttChart.vue'
import NotifPanel from './NotifPanel.vue'
import TaskForm   from './TaskForm.vue'

const TABS = [
  { key:'tasks', label:'태스크 목록' },
  { key:'gantt', label:'간트 차트' },
  { key:'notif', label:'알림 설정' },
]

export default {
  name: 'WBSDetail',
  components: { TaskTable, GanttChart, NotifPanel, TaskForm },
  props: { project: Object, logs: Array },
  emits: ['back', 'edit-project', 'toast', 'reload-logs', 'refresh-projects'],
  data() {
    return {
      tasks: [], activeTab: 'tasks', showForm: false,
      editingTask: null, taskSearch: '', TABS,
      isUploading: false, showUploadMenu: false,
      showSheetsModal: false, sheetsUrl: '', sheetsName: '',
      focusOverdueAt: 0,
      tasksLoading: true,
    }
  },
  async mounted() {
    await this.loadTasks()
    document.addEventListener('click', this.closeUploadMenu)
  },
  beforeUnmount() {
    document.removeEventListener('click', this.closeUploadMenu)
  },
  watch: { project() { this.loadTasks() } },
  methods: {
    async loadTasks() {
      this.tasksLoading = true
      this.tasks = await api.getTasks(this.project.id)
      this.tasksLoading = false
    },
    cnt(s) { return this.tasks.filter(t => getStatus(t) === s).length },
    openAdd()      { this.editingTask = null; this.showForm = true },
    openEdit(task) { this.editingTask = {...task}; this.showForm = true },

    focusOverdue() {
      if (!this.cnt('overdue')) return
      if (this.activeTab !== 'tasks') this.activeTab = 'tasks'
      this.$nextTick(() => { this.focusOverdueAt++ })
    },

    closeUploadMenu(e) {
      if (this.$refs.uploadWrap && !this.$refs.uploadWrap.contains(e.target)) {
        this.showUploadMenu = false
      }
    },

    downloadTemplate() {
      const headers = ['Group', 'Task', 'Subtask', 'Note', 'JIRA', 'Team', 'Assignee', 'Start Date', 'End Date', 'Progress']
      const sample = [
        ['기획', '', '신규 기능 기획서 작성', '요구사항 정의 포함', 'PROJ-001', '기획팀', '기획자1', '2025-10-17', '2025-10-27', '100'],
        ['디자인', '', 'UI 화면 설계', '와이어프레임 포함', '', '디자인팀', '디자인1', '2025-10-20', '2025-11-05', '80'],
        ['개발(BE)', '', 'API 개발', '', 'PROJ-002', '개발(BE)팀', '백엔드1', '2025-11-01', '2025-11-20', '60'],
        ['개발(FE)', '', 'UI 구현', '', '', '개발(FE)팀', '프론트1', '2025-11-10', '2025-11-30', '0'],
        ['QA', '', '기능 테스트', '', '', 'QA팀', 'QA1', '2025-12-01', '2025-12-10', '0'],
      ]
      const sep = '\r\n'
      const rows = [headers, ...sample].map(r => r.map(v => '"' + String(v).replace(/"/g, '""') + '"').join(',')).join(sep)
      const blob = new Blob(['\uFEFF' + rows], { type: 'text/csv;charset=utf-8;' })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url; a.download = 'wbs_업로드_양식.csv'
      a.click(); URL.revokeObjectURL(url)
    },

    async saveTask(form) {
      if (form.id) await api.updateTask(this.project.id, form.id, form)
      else         await api.createTask(this.project.id, form)
      this.showForm = false
      await this.loadTasks()
      this.$emit('refresh-projects')
      this.$emit('toast', { msg: form.id ? '태스크가 수정되었습니다' : '태스크가 추가되었습니다', type:'ok' })
    },
    async deleteTask(tid) {
      await api.deleteTask(this.project.id, tid)
      this.showForm = false
      await this.loadTasks()
      this.$emit('refresh-projects')
      this.$emit('toast', { msg:'삭제되었습니다', type:'info' })
    },

    async handleFileUpload(event) {
      const file = event.target.files[0]
      if (!file) return
      this.isUploading = true
      try {
        const res = await api.uploadExcel(this.project.id, file)
        this.$emit('toast', { msg: res.count + '개 태스크 등록 완료', type: 'ok' })
        await this.loadTasks(); this.$emit('refresh-projects')
      } catch (e) {
        this.$emit('toast', { msg: '업로드 실패: ' + e.message, type: 'err' })
      } finally {
        this.isUploading = false; event.target.value = ''
      }
    },

    async handleSheetsUpload() {
      if (!this.sheetsUrl.trim()) {
        this.$emit('toast', { msg: 'URL을 입력하세요', type: 'err' }); return
      }
      const csvUrl = this.sheetsToCsvUrl(this.sheetsUrl, this.sheetsName)
      if (!csvUrl) {
        this.$emit('toast', { msg: '올바른 Google Sheets URL이 아닙니다', type: 'err' }); return
      }
      this.isUploading = true
      try {
        const res = await api.uploadSheetsUrl(this.project.id, csvUrl)
        this.$emit('toast', { msg: res.count + '개 태스크 등록 완료', type: 'ok' })
        this.showSheetsModal = false; this.sheetsUrl = ''; this.sheetsName = ''
        await this.loadTasks(); this.$emit('refresh-projects')
      } catch (e) {
        this.$emit('toast', { msg: '가져오기 실패: ' + e.message, type: 'err' })
      } finally { this.isUploading = false }
    },

    sheetsToCsvUrl(url, sheetName) {
      const match = url.match(/spreadsheets\/d\/([a-zA-Z0-9-_]+)/)
      if (!match) return null
      const id = match[1]
      const gidMatch = url.match(/gid=(\d+)/)
      const gid = gidMatch ? gidMatch[1] : '0'
      return 'https://docs.google.com/spreadsheets/d/' + id + '/export?format=csv&gid=' + gid
    },
  }
}
</script>

<style scoped>
.detail-bar { background:var(--bg2); border-bottom:1px solid var(--border); padding:14px 24px; display:flex; align-items:center; justify-content:space-between; gap:12px }
.breadcrumb { display:flex; align-items:center; gap:10px; font-size:14px }
.bc-link    { color:var(--amber); cursor:pointer }
.bc-link:hover{ text-decoration:underline }
.bc-sep     { color:var(--faint) }
.bc-cur     { color:var(--text); font-weight:600 }
.bar-right  { display:flex; align-items:center; gap:10px }
.inner-search{ display:flex; align-items:center; gap:8px; background:var(--bg3); border:1px solid var(--border2); border-radius:8px; padding:7px 12px }
.inner-search input{ background:transparent; border:none; outline:none; color:var(--text); font-size:13px; width:180px; font-family:inherit }
.inner-search input::placeholder{ color:var(--muted) }
.detail-body{ padding:20px 24px }

.metrics  { display:grid; grid-template-columns:repeat(4,1fr); gap:12px; margin-bottom:20px }
.mc       { background:var(--bg2); border:1px solid var(--border); border-radius:10px; padding:16px 20px }
.mc-label { font-size:12px; color:var(--muted); text-transform:uppercase; letter-spacing:.05em; margin-bottom:6px; display:flex; align-items:center; gap:6px }
.mc-hint  { font-size:10px; color:var(--muted); font-weight:400; text-transform:none; letter-spacing:0 }
.mc-val   { font-size:26px; font-family:'DM Mono',monospace; font-weight:600 }
.mc-sub   { font-size:11px; color:var(--muted); margin-top:4px }
.mc-arrow { font-size:11px }
.mc-clickable { cursor:pointer; transition:background .15s; user-select:none }
.mc-clickable:hover { background:var(--bg3) }

.tabs { display:flex; gap:4px; background:var(--bg2); border:1px solid var(--border); border-radius:10px; padding:5px; width:fit-content; margin-bottom:16px }
.tab  { padding:8px 20px; border-radius:8px; cursor:pointer; font-size:14px; color:var(--muted); transition:all .15s; font-weight:500 }
.tab.on { background:var(--bg4); color:var(--text) }

.btn        { display:inline-flex; align-items:center; gap:6px; padding:7px 14px; border-radius:7px; font-size:13px; font-family:inherit; cursor:pointer; border:none; font-weight:500; transition:all .15s }
.btn-primary{ background:var(--amber); color:#0a0800 }.btn-primary:hover{ background:#f0b85a }
.btn-ghost  { background:transparent; color:var(--muted); border:1px solid var(--border2) }.btn-ghost:hover{ background:var(--bg3); color:var(--text) }
.btn-sm     { padding:6px 12px; font-size:12px }
.btn:disabled{ opacity:.5; cursor:not-allowed }

.upload-wrap { position:relative }
.upload-menu {
  position:absolute; right:0; top:36px;
  background:var(--bg2); border:1px solid var(--border2);
  border-radius:8px; padding:4px; z-index:200; min-width:180px;
  box-shadow:0 2px 8px rgba(0,0,0,.12);
  display:flex; flex-direction:column; gap:2px
}
.upload-item { width:100%; background:none; border:none; padding:9px 12px; text-align:left; color:var(--text); font-size:13px; cursor:pointer; border-radius:6px; font-family:inherit; font-weight:500 }
.upload-item:hover { background:var(--bg3) }
.upload-divider { height:1px; background:var(--border); margin:3px 0 }

.overlay { position:fixed; inset:0; background:rgba(0,0,0,.5); z-index:300; display:flex; align-items:center; justify-content:center }
.modal   { background:var(--bg2); border:1px solid var(--border2); border-radius:12px; padding:24px; width:480px; max-width:90vw }
.modal-title { font-size:15px; font-weight:600; margin-bottom:8px }
.modal-desc  { font-size:12px; color:var(--muted); margin-bottom:16px; line-height:1.6 }
.field       { margin-bottom:12px }
.field label { display:block; font-size:11px; color:var(--muted); margin-bottom:4px }
.field input { width:100%; background:var(--bg3); border:1px solid var(--border2); border-radius:6px; padding:8px 10px; color:var(--text); font-size:13px; font-family:inherit; outline:none }
.field input:focus { border-color:var(--amber) }
.modal-actions { display:flex; justify-content:flex-end; gap:8px; margin-top:16px }
</style>