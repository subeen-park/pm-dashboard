<template>
  <div class="app">
    <!-- 서버 연결 중 오버레이 -->
    <div v-if="serverWaking" class="waking-overlay">
      <div class="waking-box">
        <div class="waking-spinner"></div>
        <div class="waking-title">서버에 연결 중...</div>
        <div class="waking-sub">최초 접속 시 잠시 걸릴 수 있어요 (약 30초)</div>
        <div class="waking-dots"><span></span><span></span><span></span></div>
      </div>
    </div>

    <header class="gnb">
      <div class="logo" @click="goHome" style="cursor:pointer;">
        <div class="logo-dot"></div>PM Suite
      </div>
      <nav class="gnb-nav">
        <div class="gnb-item" :class="{active: view==='home'}" @click="goHome">홈</div>
        <div class="gnb-item" :class="{active: view==='list' || view==='detail'}" @click="goList">WBS 보드</div>
        <div class="gnb-item gnb-sub" v-if="view==='detail' && selectedProject">› {{ selectedProject.name }}</div>
        <div class="gnb-item" :class="{active: view==='calendar'}" @click="goPage('calendar')">릴리즈 캘린더</div>
        <div class="gnb-item" :class="{active: view==='checklist'}" @click="goPage('checklist')">체크리스트</div>
        <div class="gnb-item" :class="{active: view==='merge'}" @click="goPage('merge')">머지 트래커</div>
        <div class="gnb-item" :class="{active: view==='jira'}" @click="goPage('jira')">Jira 레이더</div>
      </nav>
      <div class="gnb-right">
        <span class="last-saved">{{ lastSaved }}</span>
        <a href="https://github.com/subeen-park" target="_blank" class="github-btn" title="GitHub">
          <svg viewBox="0 0 24 24" width="18" height="18" fill="currentColor">
            <path d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.531 1.032 1.531 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z"/>
          </svg>
        </a>
        <button class="theme-btn" @click="toggleTheme" :title="theme==='dark'?'라이트 모드':'다크 모드'">
          {{ theme==='dark' ? '☀️' : '🌙' }}
        </button>
        <button v-if="view==='list'||view==='detail'" class="btn btn-primary btn-sm" @click="showProjectForm=true">+ 새 WBS</button>
      </div>
    </header>

    <!-- 홈 랜딩 -->
    <div v-if="view==='home'" class="home-page">
      <div class="home-hero">
        <div class="home-badge">PM Suite</div>
        <h1 class="home-title">릴리즈부터 Jira까지,<br>PM 업무를 한 곳에서</h1>
        <p class="home-desc">WBS 관리, 머지/빌드 추적, Jira 정체 분석을<br>하나의 대시보드에서 통합 관리하세요.</p>
        <button class="btn btn-primary home-cta" @click="goList">WBS 보드 시작하기 →</button>
      </div>
      <div class="home-cards">
        <div class="home-card" @click="goList">
          <div class="home-card-icon">📋</div>
          <div class="home-card-title">WBS 보드</div>
          <div class="home-card-desc">WBS 프로젝트와 태스크를 관리하고, 간트 차트로 일정을 시각화해요. 지연/리스크 현황을 한눈에 파악하세요.</div>
          <div class="home-card-action">시작하기 →</div>
        </div>
        <div class="home-card" @click="goPage('calendar')">
          <div class="home-card-icon">📅</div>
          <div class="home-card-title">릴리즈 캘린더</div>
          <div class="home-card-desc">전체 프로젝트의 마감일과 마일스톤을 월별 캘린더로 확인하세요. 릴리즈 일정 충돌을 사전에 파악할 수 있어요.</div>
          <div class="home-card-action">확인하기 →</div>
        </div>
        <div class="home-card" @click="goPage('checklist')">
          <div class="home-card-icon">✅</div>
          <div class="home-card-title">릴리즈 체크리스트</div>
          <div class="home-card-desc">릴리즈 전 QA, 배포, 롤백 플랜 등 필수 확인 항목을 팁별로 관리하세요. 팀원이 직접 체크하는 협업 철스팅 도구입니다.</div>
          <div class="home-card-action">확인하기 →</div>
        </div>
        <div class="home-card" @click="goPage('merge')">
          <div class="home-card-icon">🔀</div>
          <div class="home-card-title">머지 트래커</div>
          <div class="home-card-desc">릴리즈 버전별 머지/빌드 현황을 플랫폼별로 추적해요. 미빌드, 빌드완료, 머지 상태를 실시간으로 확인하세요.</div>
          <div class="home-card-action">확인하기 →</div>
        </div>
        <div class="home-card" @click="goPage('jira')">
          <div class="home-card-icon">🎯</div>
          <div class="home-card-title">Jira 레이더</div>
          <div class="home-card-desc">Jira 티켓의 정체 구간을 분석하고, 병목 담당자 Top 10을 추적해요. 일정 리스크를 사전에 파악하세요.</div>
          <div class="home-card-action">분석하기 →</div>
        </div>
      </div>
    </div>

    <w-b-s-list v-if="view==='list'" :projects="projects" :loading="projectsLoading"
      @select="selectProject" @new="showProjectForm=true" @edit="editProj" @delete="deleteProject" />
    <w-b-s-detail v-if="view==='detail' && selectedProject" :project="selectedProject" :logs="logs"
      @back="goList" @edit-project="editProj" @toast="showToast" @reload-logs="loadLogs" @refresh-projects="loadProjects" />
    <merge-tracker    v-if="view==='merge'" />
    <jira-radar       v-if="view==='jira'" />
    <release-calendar v-if="view==='calendar'" />
    <release-checklist v-if="view==='checklist'" />

    <project-form v-model="showProjectForm" :edit-project="editingProject" @save="saveProject" @delete="deleteProject" />

    <div class="toast-wrap">
      <div v-for="t in toasts" :key="t.id" class="toast" :class="'toast-'+t.type">{{ t.msg }}</div>
    </div>
  </div>
</template>

<script>
import { api } from './api/index.js'
import WBSList           from './components/WBSList.vue'
import WBSDetail         from './components/WBSDetail.vue'
import ProjectForm       from './components/ProjectForm.vue'
import MergeTracker      from './components/MergeTracker.vue'
import JiraRadar         from './components/JiraRadar.vue'
import ReleaseCalendar   from './components/ReleaseCalendar.vue'
import ReleaseChecklist  from './components/ReleaseChecklist.vue'

export default {
  name: 'App',
  components: { WBSList, WBSDetail, ProjectForm, MergeTracker, JiraRadar, ReleaseCalendar, ReleaseChecklist },
  data() {
    return {
      view: 'home',
      projects: [], selectedProject: null, logs: [],
      showProjectForm: false, editingProject: null,
      lastSaved: '', toasts: [],
      theme: 'light',
      projectsLoading: true,
      serverWaking: false,
    }
  },
  async mounted() {
    const savedTheme = localStorage.getItem('wbs-theme') || 'light'
    this.setTheme(savedTheme)
    await this.loadWithWakeup()
    await this.loadLogs()
    window.addEventListener('hashchange', this.onHashChange)
    // 초기 해시 설정
    if (!location.hash || location.hash === '#') {
      location.hash = 'home'
    }
    this.applyHash()
  },
  beforeUnmount() {
    window.removeEventListener('hashchange', this.onHashChange)
  },
  methods: {
    async loadWithWakeup() {
      // 서버 깨우기 시도 (타임아웃 3초 안에 응답 없으면 waking 표시)
      const wakeTimer = setTimeout(() => { this.serverWaking = true }, 3000)
      try {
        await this.loadProjects()
      } finally {
        clearTimeout(wakeTimer)
        this.serverWaking = false
      }
    },
    async loadProjects() {
      this.projectsLoading = true
      try {
        this.projects = await api.getProjects()
        this.lastSaved = new Date().toLocaleTimeString('ko', { hour:'2-digit', minute:'2-digit' }) + ' 업데이트'
        if (this.selectedProject) {
          const updated = this.projects.find(p => p.id === this.selectedProject.id)
          if (updated) this.selectedProject = updated
        }
      } catch(e) {
        console.error(e)
      } finally {
        this.projectsLoading = false
      }
    },
    async loadLogs() { try { this.logs = await api.getLogs() } catch(e) {} },
    selectProject(proj) {
      this.selectedProject = proj; this.view = 'detail'
      location.hash = 'detail'
    },
    goHome() { this.view = 'home'; this.selectedProject = null; location.hash = 'home' },
    goList() { this.view = 'list'; this.selectedProject = null; location.hash = 'list' },
    goPage(page) { this.view = page; this.selectedProject = null; location.hash = page },
    onHashChange() {
      const hash = location.hash.replace('#', '') || 'home'
      const valid = ['home', 'list', 'detail', 'merge', 'jira', 'calendar', 'checklist']
      if (valid.includes(hash)) {
        // detail 이고 selectedProject 없으면 list로
        if (hash === 'detail' && !this.selectedProject) {
          this.view = 'list'
          location.hash = 'list'
        } else {
          this.view = hash
          if (hash !== 'detail') this.selectedProject = null
        }
      } else {
        this.view = 'home'
        location.hash = 'home'
      }
    },
    applyHash() {
      const hash = location.hash.replace('#', '') || 'home'
      const valid = ['home', 'list', 'detail', 'merge', 'jira', 'calendar', 'checklist']
      if (valid.includes(hash) && hash !== 'detail') {
        this.view = hash
      } else {
        this.view = 'home'
        location.hash = 'home'
      }
    },
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
      this.showProjectForm = false; this.editingProject = null
      await this.loadProjects()
    },
    async deleteProject(id) {
      try {
        await api.deleteProject(id)
        this.showProjectForm = false; this.editingProject = null
        this.showToast({ msg: 'WBS가 삭제되었습니다', type: 'info' })
        if (this.selectedProject?.id === id) this.goList()
        await this.loadProjects()
      } catch(e) { this.showToast({ msg: '삭제 실패: ' + e.message, type: 'err' }) }
    },
    showToast({ msg, type='info' }) {
      const id = Date.now()
      this.toasts.push({ id, msg, type })
      setTimeout(() => { this.toasts = this.toasts.filter(t => t.id !== id) }, 5000)
    },
    toggleTheme() { this.setTheme(this.theme==='dark' ? 'light' : 'dark') },
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
:root[data-theme="light"]{
  --bg:#f4f6f8;--bg2:#ffffff;--bg3:#f9fafb;--bg4:#f3f4f6;
  --amber:#f59f00;--amber-dim:#fff3bf;
  --blue:#339af0;--blue-dim:#e7f5ff;
  --green:#20c997;--green-dim:#e6fcf5;
  --red:#ff6b6b;--red-dim:#ffe3e3;
  --yellow:#fcc419;--yellow-dim:#fff9db;
  --text:#212529;--muted:#868e96;--faint:#ced4da;
  --border:#e9ecef;--border2:#dee2e6;
}

html{scroll-behavior:smooth}
body{background:var(--bg);color:var(--text);font-family:'Noto Sans KR',sans-serif;font-size:15px;min-height:100vh;transition:background .3s,color .3s}
.app{display:grid;grid-template-rows:auto 1fr;min-height:100vh}

/* GNB */
.gnb{background:var(--bg2);border-bottom:1px solid var(--border);padding:0 24px;height:60px;display:flex;align-items:center;gap:16px;position:sticky;top:0;z-index:100;transition:background .3s}
.logo{display:flex;align-items:center;gap:10px;font-family:'DM Mono',monospace;font-size:16px;font-weight:600;color:var(--amber);white-space:nowrap}
.logo-dot{width:8px;height:8px;background:var(--amber);border-radius:50%;flex-shrink:0}
.gnb-nav{display:flex;align-items:center;gap:4px;flex:1}
.gnb-item{padding:8px 16px;border-radius:8px;font-size:14px;color:var(--muted);cursor:pointer;transition:all .15s;white-space:nowrap;max-width:240px;overflow:hidden;text-overflow:ellipsis}
.gnb-item:hover{background:var(--bg3);color:var(--text)}
.gnb-item.active{background:var(--bg4);color:var(--text);font-weight:500}
.gnb-sub{color:var(--amber)!important;background:transparent!important;font-size:12px;padding:6px 8px;cursor:default}
.gnb-right{display:flex;align-items:center;gap:12px;margin-left:auto}
.last-saved{font-size:12px;color:var(--muted);white-space:nowrap}
.theme-btn{background:transparent;border:1px solid var(--border2);color:var(--text);border-radius:50%;width:34px;height:34px;display:flex;align-items:center;justify-content:center;cursor:pointer;font-size:16px;transition:all .2s}
.theme-btn:hover{background:var(--bg3);transform:scale(1.05)}
.github-btn{display:flex;align-items:center;justify-content:center;width:34px;height:34px;border-radius:50%;border:1px solid var(--border2);color:var(--muted);transition:all .2s;text-decoration:none}
.github-btn:hover{background:var(--bg3);color:var(--text);transform:scale(1.05)}

/* 버튼 */
.btn{display:inline-flex;align-items:center;gap:8px;padding:10px 18px;border-radius:8px;font-size:14px;font-family:'Noto Sans KR',sans-serif;cursor:pointer;border:none;transition:all .15s;font-weight:500}
.btn-primary{background:var(--amber);color:#0a0800}.btn-primary:hover{background:#f0b85a}
.btn-sm{padding:7px 14px;font-size:13px}

/* 서버 깨우기 오버레이 */
.waking-overlay{position:fixed;inset:0;background:rgba(0,0,0,.7);backdrop-filter:blur(4px);z-index:500;display:flex;align-items:center;justify-content:center}
.waking-box{background:var(--bg2);border:1px solid var(--border2);border-radius:16px;padding:40px 48px;text-align:center;display:flex;flex-direction:column;align-items:center;gap:16px}
.waking-spinner{width:40px;height:40px;border:3px solid var(--border2);border-top-color:var(--amber);border-radius:50%;animation:spin 1s linear infinite}
.waking-title{font-size:18px;font-weight:600;color:var(--text)}
.waking-sub{font-size:13px;color:var(--muted)}
.waking-dots{display:flex;gap:6px}
.waking-dots span{width:8px;height:8px;border-radius:50%;background:var(--amber);animation:dot-bounce .8s infinite alternate}
.waking-dots span:nth-child(2){animation-delay:.2s}
.waking-dots span:nth-child(3){animation-delay:.4s}
@keyframes spin{to{transform:rotate(360deg)}}
@keyframes dot-bounce{from{opacity:.3;transform:scale(.8)}to{opacity:1;transform:scale(1)}}

/* 홈 랜딩 */
.home-page{padding:60px 24px;max-width:1100px;margin:0 auto}
.home-hero{text-align:center;padding:60px 0 80px}
.home-badge{display:inline-block;background:var(--amber-dim);color:var(--amber);font-size:13px;font-weight:600;padding:4px 14px;border-radius:20px;margin-bottom:24px;font-family:'DM Mono',monospace}
.home-title{font-size:42px;font-weight:700;line-height:1.3;margin-bottom:20px;color:var(--text)}
.home-desc{font-size:16px;color:var(--muted);line-height:1.8;margin-bottom:36px}
.home-cta{font-size:15px;padding:14px 32px;border-radius:10px}
.home-cards{display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:20px}
.home-card{background:var(--bg2);border:1px solid var(--border);border-radius:14px;padding:28px;cursor:pointer;transition:all .2s;display:flex;flex-direction:column;gap:12px}
.home-card:hover{border-color:var(--amber);transform:translateY(-3px);box-shadow:0 8px 24px rgba(0,0,0,.12)}
.home-card-icon{font-size:32px}
.home-card-title{font-size:18px;font-weight:600;color:var(--text)}
.home-card-desc{font-size:13px;color:var(--muted);line-height:1.7;flex:1}
.home-card-action{font-size:13px;color:var(--amber);font-weight:600}

/* 토스트 */
.toast-wrap{position:fixed;bottom:24px;right:24px;z-index:300;display:flex;flex-direction:column;gap:8px}
.toast{background:var(--bg3);border:1px solid var(--border2);border-radius:8px;padding:12px 18px;font-size:14px;animation:slideIn .2s ease;min-width:260px;line-height:1.4;color:var(--text)}
.toast-ok{border-color:var(--green-dim);color:var(--green)}
.toast-err{border-color:var(--red-dim);color:var(--red)}
.toast-info{border-color:var(--blue-dim);color:var(--blue)}
@keyframes slideIn{from{transform:translateX(100%);opacity:0}to{transform:translateX(0);opacity:1}}
</style>