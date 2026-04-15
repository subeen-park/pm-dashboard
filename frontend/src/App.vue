<template>
  <div class="app">
    <header class="gnb">
      <div class="logo" @click="goList" style="cursor:pointer;">
        <div class="logo-dot"></div>PM Suite
      </div>
      <nav class="gnb-nav">
        <!-- WBS 릴리즈 보드 -->
        <div class="gnb-item" :class="{active: view==='list' || view==='detail'}" @click="goList">
          릴리즈 보드
        </div>
        <div class="gnb-item gnb-sub" v-if="view==='detail' && selectedProject">
          › {{ selectedProject.name }}
        </div>
        <!-- 머지 트래커 -->
        <div class="gnb-item" :class="{active: view==='merge'}" @click="goPage('merge')">
          머지 트래커
        </div>
        <!-- Jira 레이더 -->
        <div class="gnb-item" :class="{active: view==='jira'}" @click="goPage('jira')">
          Jira 레이더
        </div>
      </nav>
      <div class="gnb-right">
        <span class="last-saved">{{ lastSaved }}</span>
        <button class="theme-btn" @click="toggleTheme" :title="theme === 'dark' ? '라이트 모드로 보기' : '다크 모드로 보기'">
          {{ theme === 'dark' ? '☀️' : '🌙' }}
        </button>
        <button v-if="view==='list' || view==='detail'" class="btn btn-primary btn-sm" @click="showProjectForm=true">+ 새 WBS</button>
      </div>
    </header>

    <w-b-s-list
      v-if="view==='list'"
      :projects="projects"
      :loading="projectsLoading"
      @select="selectProject"
      @new="showProjectForm=true"
      @edit="editProj"
      @delete="deleteProject" 
    />
    <w-b-s-detail
      v-if="view==='detail' && selectedProject"
      :project="selectedProject"
      :logs="logs"
      @back="goList"
      @edit-project="editProj"
      @toast="showToast"
      @reload-logs="loadLogs"
      @refresh-projects="loadProjects"
    />
    <merge-tracker v-if="view==='merge'" />
    <jira-radar    v-if="view==='jira'" />

    <project-form
      v-model="showProjectForm"
      :edit-project="editingProject"
      @save="saveProject"
      @delete="deleteProject"
    />

    <div class="toast-wrap">
      <div v-for="t in toasts" :key="t.id" class="toast" :class="`toast-${t.type}`">{{ t.msg }}</div>
    </div>
  </div>
</template>

<script>
import { api } from './api/index.js'
import WBSList      from './components/WBSList.vue'
import WBSDetail    from './components/WBSDetail.vue'
import ProjectForm  from './components/ProjectForm.vue'
import MergeTracker from './components/MergeTracker.vue'
import JiraRadar    from './components/JiraRadar.vue'

export default {
  name: 'App',
  components: { WBSList, WBSDetail, ProjectForm, MergeTracker, JiraRadar },
  data() {
    return {
      view: 'list',
      projects: [],
      selectedProject: null,
      logs: [],
      showProjectForm: false,
      editingProject: null,
      lastSaved: '',
      toasts: [],
      theme: 'dark',
      projectsLoading: true,
    }
  },
  async mounted() {
    await this.loadProjects()
    await this.loadLogs()
    const savedTheme = localStorage.getItem('wbs-theme') || 'dark'
    this.setTheme(savedTheme)
  },
  methods: {
    async loadProjects() {
      this.projectsLoading = true
      this.projects = await api.getProjects()
      this.projectsLoading = false
      this.lastSaved = new Date().toLocaleTimeString('ko', { hour:'2-digit', minute:'2-digit' }) + ' 업데이트'
      if (this.selectedProject) {
        const updated = this.projects.find(p => p.id === this.selectedProject.id)
        if (updated) this.selectedProject = updated
      }
    },
    async loadLogs() { this.logs = await api.getLogs() },
    selectProject(proj) { this.selectedProject = proj; this.view = 'detail' },
    goList() { this.view = 'list'; this.selectedProject = null },
    goPage(page) { this.view = page; this.selectedProject = null },
    editProj(proj) { this.editingProject = {...proj}; this.showProjectForm = true },

    async saveProject(form) {
      if (form.id) {
        await api.updateProject(form.id, form)
        this.showToast({ msg: 'WBS가 수정되었습니다', type: 'ok' })
        if (this.selectedProject?.id === form.id) this.selectedProject = { ...this.selectedProject, ...form }
      } else {
        await api.createProject(form)
        this.showToast({ msg: 'WBS가 등록되었습니다', type: 'ok' })
      }
      this.showProjectForm = false
      this.editingProject = null
      await this.loadProjects()
    },

    // 💡 프로젝트 삭제 처리 함수
    async deleteProject(id) {
      try {
        await api.deleteProject(id)
        this.showProjectForm = false
        this.editingProject = null
        this.showToast({ msg: 'WBS가 삭제되었습니다', type: 'info' })
        if (this.selectedProject?.id === id) this.goList()
        await this.loadProjects()
      } catch (e) {
        this.showToast({ msg: '삭제 실패: ' + e.message, type: 'err' })
      }
    },

    showToast({ msg, type = 'info' }) {
      const id = Date.now()
      this.toasts.push({ id, msg, type })
      setTimeout(() => { this.toasts = this.toasts.filter(t => t.id !== id) }, 5000)
    },
    toggleTheme() {
      const newTheme = this.theme === 'dark' ? 'light' : 'dark'
      this.setTheme(newTheme)
    },
    setTheme(t) {
      this.theme = t
      document.documentElement.setAttribute('data-theme', t) 
      localStorage.setItem('wbs-theme', t) 
    }
  }
}
</script>

<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;700&family=DM+Mono:wght@400;500&display=swap');
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}

:root{
  --bg:#09090f;--bg2:#111118;--bg3:#18181f;--bg4:#1f1f28;
  --amber:#e8a94a;--amber-dim:#7a5420;
  --blue:#4a9eff;--blue-dim:#1a3d6a;
  --green:#4ecb8d;--green-dim:#1a4a32;
  --red:#ff6b6b;--red-dim:#5a1a1a;
  --yellow:#f0c040;--yellow-dim:#5a4210;
  --text:#e2e2ec;--muted:#7070a0;--faint:#3a3a55;
  --border:#202030;--border2:#2a2a40;
}

:root[data-theme="light"] {
  --bg: #f4f6f8; --bg2: #ffffff; --bg3: #f9fafb; --bg4: #f3f4f6;
  --amber: #f59f00; --amber-dim: #fff3bf;
  --blue: #339af0; --blue-dim: #e7f5ff;
  --green: #20c997; --green-dim: #e6fcf5;
  --red: #ff6b6b; --red-dim: #ffe3e3;
  --yellow: #fcc419; --yellow-dim: #fff9db;
  --text: #212529; --muted: #868e96; --faint: #ced4da;
  --border: #e9ecef; --border2: #dee2e6;
}

html{scroll-behavior:smooth}
body{background:var(--bg);color:var(--text);font-family:'Noto Sans KR',sans-serif;font-size:15px;min-height:100vh;transition: background 0.3s, color 0.3s;}
.app{display:grid;grid-template-rows:auto 1fr;min-height:100vh}
.gnb{background:var(--bg2);border-bottom:1px solid var(--border);padding:0 24px;height:60px;display:flex;align-items:center;gap:16px;position:sticky;top:0;z-index:100;transition: background 0.3s;}
.logo{display:flex;align-items:center;gap:10px;font-family:'DM Mono',monospace;font-size:16px;font-weight:600;color:var(--amber);white-space:nowrap}
.logo-dot{width:8px;height:8px;background:var(--amber);border-radius:50%;flex-shrink:0}
.gnb-nav{display:flex;align-items:center;gap:4px;flex:1}
.gnb-item{padding:8px 16px;border-radius:8px;font-size:14px;color:var(--muted);cursor:pointer;transition:all .15s;white-space:nowrap;max-width:240px;overflow:hidden;text-overflow:ellipsis}
.gnb-item:hover{background:var(--bg3);color:var(--text)}
.gnb-item.active{background:var(--bg4);color:var(--text);font-weight:500;}
.gnb-sub{color:var(--amber)!important;background:transparent!important;font-size:12px;padding:6px 8px;cursor:default}
.gnb-right{display:flex;align-items:center;gap:12px;margin-left:auto}
.last-saved{font-size:12px;color:var(--muted);white-space:nowrap}

.theme-btn {
  background: transparent; border: 1px solid var(--border2); color: var(--text);
  border-radius: 50%; width: 34px; height: 34px;
  display: flex; align-items: center; justify-content: center;
  cursor: pointer; font-size: 16px; transition: all 0.2s;
}
.theme-btn:hover { background: var(--bg3); transform: scale(1.05); }

.btn{display:inline-flex;align-items:center;gap:8px;padding:10px 18px;border-radius:8px;font-size:14px;font-family:'Noto Sans KR',sans-serif;cursor:pointer;border:none;transition:all .15s;font-weight:500}
.btn-primary{background:var(--amber);color:#0a0800}.btn-primary:hover{background:#f0b85a}
.btn-sm{padding:7px 14px;font-size:13px}

.toast-wrap{position:fixed;bottom:24px;right:24px;z-index:300;display:flex;flex-direction:column;gap:8px}
.toast{background:var(--bg3);border:1px solid var(--border2);border-radius:8px;padding:12px 18px;font-size:14px;animation:slideIn .2s ease;min-width:260px; line-height: 1.4; color:var(--text)}
.toast-ok{border-color:var(--green-dim);color:var(--green)}
.toast-err{border-color:var(--red-dim);color:var(--red)}
.toast-info{border-color:var(--blue-dim);color:var(--blue)}

@keyframes slideIn{from{transform:translateX(100%);opacity:0}to{transform:translateX(0);opacity:1}}
</style>