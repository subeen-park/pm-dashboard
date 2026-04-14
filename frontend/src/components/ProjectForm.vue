<template>
  <div v-if="modelValue" class="overlay" @click.self="$emit('update:modelValue', false)">
    <div class="modal">
      <div class="modal-title">{{ editProject ? 'WBS 수정' : '새 WBS 등록' }}</div>
      <div class="field">
        <label>프로젝트명 *</label>
        <input v-model="form.name" placeholder="예: 신규 캐릭터 출시 v1.0" />
      </div>
      <div class="field">
        <label>설명</label>
        <input v-model="form.description" placeholder="간단한 설명 (선택)" />
      </div>
      <div class="row2">
        <div class="field">
          <label>담당 PM</label>
          <input v-model="form.pm" placeholder="예: 박수빈" />
        </div>
        <div class="field">
          <label>마감일</label>
          <input type="date" v-model="form.endDate" />
        </div>
      </div>
      <div class="modal-actions">
        <button v-if="editProject" class="btn btn-danger" @click="remove">삭제</button>
        <div style="flex:1"></div>
        <button class="btn btn-ghost" @click="$emit('update:modelValue', false)">취소</button>
        <button class="btn btn-primary" @click="submit">{{ editProject ? '저장' : '등록' }}</button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ProjectForm',
  props: { modelValue: Boolean, editProject: Object },
  emits: ['update:modelValue', 'save', 'delete'],
  data() { return { form: { name:'', description:'', pm:'', endDate:'' } } },
  watch: {
    editProject(val) { this.form = val ? {...val} : { name:'', description:'', pm:'', endDate:'' } },
    modelValue(v)    { if (v && !this.editProject) this.form = { name:'', description:'', pm:'', endDate:'' } }
  },
  methods: {
    submit() {
      if (!this.form.name.trim()) { alert('프로젝트명을 입력하세요'); return }
      this.$emit('save', { ...this.form, id: this.editProject?.id })
    },
    remove() {
      if (!confirm('이 WBS를 삭제하시겠습니까?\n(포함된 태스크도 모두 삭제됩니다)')) return
      this.$emit('delete', this.editProject.id)
    }
  }
}
</script>

<style scoped>
.overlay{ position:fixed; inset:0; background:rgba(0,0,0,.6); z-index:200; display:flex; align-items:center; justify-content:center }
.modal  { background:var(--bg2); border:1px solid var(--border2); border-radius:12px; padding:24px; width:480px; max-width:90vw }
.modal-title{ font-size:16px; font-weight:500; margin-bottom:18px }
.field  { margin-bottom:12px }
.field label{ display:block; font-size:11px; color:var(--muted); margin-bottom:5px }
.field input{ width:100%; background:var(--bg3); border:1px solid var(--border2); border-radius:6px; padding:8px 10px; color:var(--text); font-size:13px; font-family:inherit; outline:none }
.field input:focus{ border-color:var(--amber) }
.row2  { display:grid; grid-template-columns:1fr 1fr; gap:10px }
.modal-actions{ display:flex; align-items:center; gap:8px; margin-top:18px }
.btn   { display:inline-flex; align-items:center; padding:7px 16px; border-radius:7px; font-size:13px; cursor:pointer; border:none; font-family:inherit; font-weight:500 }
.btn-primary{ background:var(--amber); color:#0a0800 }
.btn-primary:hover{ background:#f0b85a }
.btn-ghost  { background:transparent; color:var(--muted); border:1px solid var(--border2) }
.btn-ghost:hover{ background:var(--bg3); color:var(--text) }
.btn-danger { background:transparent; color:var(--red); border:1px solid var(--red-dim) }
.btn-danger:hover{ background:var(--red-dim) }
</style>
