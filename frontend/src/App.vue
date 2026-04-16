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
      <div class="logo" @click="goHome" style="cursor:pointer;">PM Suite</div>
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
        <p class="home-eyebrow">PM Suite &mdash; 릴리즈 관리 도구</p>
        <h1 class="home-title">PM 업무를<br>한 곳에서.</h1>
        <p class="home-desc">WBS 관리, 릴리즈 캘린더, 체크리스트,<br>머지 추적, Jira 분석을 통합하세요.</p>
        <button class="btn btn-primary home-cta" @click="goList">WBS 보드 시작하기</button>
      </div>
      <div class="home-divider"></div>
      <div class="home-cards">
        <div class="home-card" @click="goList">
          <div class="home-card-num">01</div>
          <div class="home-card-title">WBS 보드</div>
          <div class="home-card-desc">프로젝트와 태스크를 관리하고 간트 차트로 일정을 시각화</div>
          <div class="home-card-action">시작하기</div>
        </div>
        <div class="home-card" @click="goPage('calendar')">
          <div class="home-card-num">02</div>
          <div class="home-card-title">릴리즈 캘린더</div>
          <div class="home-card-desc">전체 프로젝트 마감일과 마일스톤을 월별 캘린더로 확인</div>
          <div class="home-card-action">확인하기</div>
        </div>
        <div class="home-card" @click="goPage('checklist')">
          <div class="home-card-num">03</div>
          <div class="home-card-title">릴리즈 체크리스트</div>
          <div class="home-card-desc">릴리즈 전 QA, 배포, 롤백 플랜 등 팀 협업 체크리스트</div>
          <div class="home-card-action">확인하기</div>
        </div>
        <div class="home-card" @click="goPage('merge')">
          <div class="home-card-num">04</div>
          <div class="home-card-title">머지 트래커</div>
          <div class="home-card-desc">버전별 머지/빌드 현황을 플랫폼별로 실시간 추적</div>
          <div class="home-card-action">확인하기</div>
        </div>
        <div class="home-card" @click="goPage('jira')">
          <div class="home-card-num">05</div>
          <div class="home-card-title">Jira 레이더</div>
          <div class="home-card-desc">Jira 티켓 정체 구간과 병목 담당자 Top 10 분석</div>
          <div class="home-card-action">분석하기</div>
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
  --bg:#07070e;--bg2:#0e0e18;--bg3:#141420;--bg4:#1a1a28;
  --amber:#c8d878;--amber-dim:rgba(200,216,120,.1);
  --blue:#4a9eff;--blue-dim:rgba(74,158,255,.1);
  --green:#3db87a;--green-dim:rgba(61,184,122,.1);
  --red:#e05555;--red-dim:rgba(224,85,85,.1);
  --yellow:#d4a843;--yellow-dim:rgba(212,168,67,.1);
  --text:#eeeeee;--muted:#9090a8;--faint:#2a2a40;
  --border:rgba(255,255,255,.07);--border2:rgba(255,255,255,.14);
}
:root[data-theme="light"]{
  --bg:#f5f5f0;--bg2:#ffffff;--bg3:#f8f8f4;--bg4:#efefea;
  --amber:#1a1a1a;--amber-dim:rgba(0,0,0,.06);
  --blue:#2b7fd4;--blue-dim:rgba(43,127,212,.08);
  --green:#1a9660;--green-dim:rgba(26,150,96,.08);
  --red:#cc3333;--red-dim:rgba(204,51,51,.08);
  --yellow:#b08820;--yellow-dim:rgba(176,136,32,.08);
  --text:#1a1a24;--muted:#888898;--faint:#d8d8d0;
  --border:rgba(0,0,0,.07);--border2:rgba(0,0,0,.14);
}

html{scroll-behavior:smooth}
body{background:var(--bg);color:var(--text);font-family:'Noto Sans KR',sans-serif;font-size:16px;min-height:100vh;transition:background .3s,color .3s;-webkit-font-smoothing:antialiased}
.app{display:grid;grid-template-rows:auto 1fr;min-height:100vh}

/* GNB */
.gnb{background:var(--bg);border-bottom:1px solid var(--border);padding:0 32px;height:56px;display:flex;align-items:center;gap:0;position:sticky;top:0;z-index:100;transition:background .3s}
.logo{font-family:'DM Mono',monospace;font-size:13px;font-weight:500;color:var(--amber);letter-spacing:.08em;text-transform:uppercase;white-space:nowrap;margin-right:40px}
.gnb-nav{display:flex;align-items:stretch;gap:0;flex:1;height:100%}
.gnb-item{padding:0 16px;font-size:13px;color:var(--muted);cursor:pointer;transition:color .15s;white-space:nowrap;display:flex;align-items:center;position:relative;border-bottom:2px solid transparent}
.gnb-item:hover{color:var(--text)}
.gnb-item.active{color:var(--text);border-bottom-color:var(--amber)}
.gnb-sub{color:var(--amber)!important;border-bottom:none!important;font-size:12px;cursor:default;opacity:.8}
.gnb-right{display:flex;align-items:center;gap:10px;margin-left:auto}
.last-saved{font-size:11px;color:var(--muted);white-space:nowrap}
.theme-btn{background:transparent;border:1px solid var(--border2);color:var(--muted);border-radius:6px;width:32px;height:32px;display:flex;align-items:center;justify-content:center;cursor:pointer;font-size:14px;transition:all .15s}
.theme-btn:hover{color:var(--text);border-color:var(--border2)}
.github-btn{display:flex;align-items:center;justify-content:center;width:32px;height:32px;border-radius:6px;border:1px solid var(--border2);color:var(--muted);transition:all .15s;text-decoration:none}
.github-btn:hover{color:var(--text)}

/* 버튼 */
.btn{display:inline-flex;align-items:center;gap:8px;padding:9px 18px;border-radius:6px;font-size:13px;font-family:'Noto Sans KR',sans-serif;cursor:pointer;border:none;transition:all .15s;font-weight:500;letter-spacing:.01em}
.btn-primary{background:var(--amber);color:#fff}.btn-primary:hover{opacity:.85}
:root[data-theme="light"] .btn-primary{color:#fff}
.btn-sm{padding:6px 14px;font-size:12px}

/* 서버 깨우기 오버레이 */
.waking-overlay{position:fixed;inset:0;background:rgba(0,0,0,.75);backdrop-filter:blur(8px);z-index:500;display:flex;align-items:center;justify-content:center}
.waking-box{background:var(--bg2);border:1px solid var(--border2);border-radius:12px;padding:40px 52px;text-align:center;display:flex;flex-direction:column;align-items:center;gap:16px}
.waking-spinner{width:32px;height:32px;border:2px solid var(--border2);border-top-color:var(--amber);border-radius:50%;animation:spin 1s linear infinite}
.waking-title{font-size:16px;font-weight:600;color:var(--text)}
.waking-sub{font-size:12px;color:var(--muted)}
.waking-dots{display:flex;gap:5px}
.waking-dots span{width:6px;height:6px;border-radius:50%;background:var(--amber);animation:dot-bounce .8s infinite alternate}
.waking-dots span:nth-child(2){animation-delay:.2s}
.waking-dots span:nth-child(3){animation-delay:.4s}
@keyframes spin{to{transform:rotate(360deg)}}
@keyframes dot-bounce{from{opacity:.3;transform:scale(.8)}to{opacity:1;transform:scale(1)}}

/* 홈 - 노스크롤 레이아웃 */
.home-page{height:calc(100vh - 56px);display:flex;flex-direction:column;padding:64px 56px 48px;max-width:1300px;margin:0 auto;box-sizing:border-box;overflow:hidden}
.home-hero{max-width:720px;flex-shrink:0}
.home-eyebrow{font-size:11px;font-weight:500;letter-spacing:.16em;text-transform:uppercase;color:var(--muted);margin-bottom:20px}
.home-title{font-size:56px;font-weight:700;line-height:1.1;margin-bottom:16px;color:var(--text);letter-spacing:-.025em}
.home-desc{font-size:15px;color:var(--muted);line-height:1.75;margin-bottom:28px;font-weight:300}
.home-cta{font-size:13px;padding:10px 22px;border-radius:6px}
.home-divider{display:none}
.home-cards{margin-top:auto;display:grid;grid-template-columns:repeat(5,1fr);gap:1px;background:var(--border);border:1px solid var(--border);border-radius:10px;overflow:hidden;flex-shrink:0}
.home-card{background:var(--bg2);padding:22px 20px;cursor:pointer;transition:background .15s;display:flex;flex-direction:column;gap:10px;position:relative}
.home-card:hover{background:var(--bg3)}
.home-card-num{font-size:10px;font-family:'DM Mono',monospace;color:var(--muted);letter-spacing:.1em}
.home-card-title{font-size:14px;font-weight:600;color:var(--text);line-height:1.3}
.home-card-desc{font-size:12px;color:var(--muted);line-height:1.6;flex:1}
.home-card-action{font-size:11px;color:var(--amber);font-weight:600;letter-spacing:.04em;text-transform:uppercase;margin-top:4px}

/* 토스트 */
.toast-wrap{position:fixed;bottom:24px;right:24px;z-index:400;display:flex;flex-direction:column;gap:8px}
.toast{background:var(--bg2);border:1px solid var(--border2);border-radius:8px;padding:12px 18px;font-size:13px;animation:slideIn .2s ease;min-width:240px;line-height:1.5;color:var(--text)}
.toast-ok{border-left:3px solid var(--green)}
.toast-err{border-left:3px solid var(--red)}
.toast-info{border-left:3px solid var(--blue)}
@keyframes slideIn{from{transform:translateX(100%);opacity:0}to{transform:translateX(0);opacity:1}}
</style>