<template>
  <div class="flex flex-col space-y-4 flex-1">
    <HeaderView :headerTitle="headerTitle" />

    <!-- Feedback messages -->
    <div v-if="successMsg" class="p-3 px-4 rounded-2xl text-sm bg-green-100 border border-green-400 text-green-800">
      {{ successMsg }}
    </div>
    <div v-if="errorMsg" class="p-3 px-4 rounded-2xl text-sm bg-red-100 border border-red-400 text-red-800">
      {{ errorMsg }}
    </div>

    <!-- Upload card (admin only) -->
    <div v-if="isAdmin" class="rounded-2xl border border-gray-100 shadow-sm bg-white p-6 space-y-4">
      <h2 class="text-lg font-bold text-gray-800">Upload New Template</h2>
      <p class="text-sm text-gray-500">
        Upload a PowerPoint, Word, or PDF template that presenters can download.
        Accepted formats: <strong>.ppt .pptx .doc .docx .pdf .zip</strong>. Max 50 MB.
      </p>

      <div class="grid sm:grid-cols-2 gap-4">
        <div>
          <label class="block text-xs font-semibold text-gray-600 mb-1.5 uppercase tracking-wide">
            File
          </label>
          <input type="file"
            accept=".ppt,.pptx,.doc,.docx,.pdf,.zip"
            @change="onFileSelected"
            ref="fileInput"
            class="block w-full text-sm text-gray-700 border border-gray-200 rounded-xl px-3 py-2
                   file:mr-4 file:py-1.5 file:px-4 file:rounded-full file:border-0
                   file:text-xs file:font-semibold file:text-white cursor-pointer" />
        </div>
        <div>
          <label class="block text-xs font-semibold text-gray-600 mb-1.5 uppercase tracking-wide">
            Description (optional)
          </label>
          <input v-model="newDescription" type="text" placeholder="e.g. ECSACONM 2026 oral presentation template"
            class="w-full border border-gray-200 rounded-xl px-3 py-2 text-sm focus:outline-none focus:ring-2"
            style="focus-ring-color: rgb(254,80,103);" />
        </div>
      </div>

      <button @click="uploadTemplate" :disabled="!selectedFile || isUploading"
        class="px-6 py-2 rounded-full text-sm font-semibold text-white disabled:opacity-50 transition hover:opacity-90"
        style="background-color: rgb(254,80,103);">
        {{ isUploading ? 'Uploading…' : 'Upload Template' }}
      </button>
    </div>

    <!-- Hidden file input for replacing an existing template's file -->
    <input type="file" ref="replaceFileInput" class="hidden"
      accept=".ppt,.pptx,.doc,.docx,.pdf,.zip"
      @change="onReplaceSelected" />

    <!-- Template list -->
    <div class="rounded-2xl border border-gray-100 shadow-sm bg-white overflow-hidden">
      <div class="px-4 pt-3 pb-1 text-xs text-gray-400">
        {{ templates.length }} template{{ templates.length !== 1 ? 's' : '' }}
      </div>
      <div class="flex bg-mercury-500 p-3 pt-2 pb-2 rounded-t-sm uppercase text-xs font-bold">
        <div class="w-1/12 p-1">#</div>
        <div class="w-4/12 p-1">File Name</div>
        <div class="w-3/12 p-1">Description</div>
        <div class="w-2/12 p-1">Size</div>
        <div class="w-2/12 p-1">Actions</div>
      </div>

      <SpinnerComponent v-if="isLoading" />

      <div v-else-if="templates.length === 0" class="p-8 text-center text-sm text-gray-400 italic">
        No templates uploaded yet.
      </div>

      <div v-for="(tpl, index) in templates" :key="tpl.id"
        class="flex sm:flex-row flex-col p-3 pt-2 pb-2 text-sm items-center border-t border-mercury-500">
        <div class="sm:w-1/12 w-full p-1 text-gray-400">{{ index + 1 }}</div>
        <div class="sm:w-4/12 w-full p-1 font-medium text-gray-800 truncate">
          <span class="mr-2">{{ fileIcon(tpl.original_name) }}</span>{{ tpl.original_name }}
        </div>
        <div class="sm:w-3/12 w-full p-1 text-gray-500 text-xs">{{ tpl.description || '—' }}</div>
        <div class="sm:w-2/12 w-full p-1 text-gray-500 text-xs">{{ formatSize(tpl.file_size) }}</div>
        <div class="sm:w-2/12 w-full p-1 flex gap-2">
          <a :href="`${apiUrl}/presentation_templates/${tpl.id}/download`"
            target="_blank"
            class="px-3 py-1 text-xs rounded-full font-semibold text-white transition hover:opacity-90"
            style="background-color: rgb(0,150,180);">
            Download
          </a>
          <button v-if="isAdmin" @click="replaceTemplate(tpl.id)"
            class="px-3 py-1 text-xs rounded-full font-semibold text-white transition hover:opacity-90"
            style="background-color: rgb(0,150,180);">
            Replace
          </button>
          <button v-if="isAdmin" @click="deleteTemplate(tpl.id)"
            class="px-3 py-1 text-xs rounded-full font-semibold text-white bg-red-500 hover:bg-red-400 transition">
            Delete
          </button>
        </div>
      </div>
    </div>

  </div>
</template>

<script>
import HeaderView from '@/includes/Header.vue'
import SpinnerComponent from '@/components/Spinner.vue'
import { useAuthStore } from '@/store/authStore'
import { setAuthToken } from '@/services/apiService'
import axios from 'axios'

export default {
  name: 'PresentationTemplatesView',
  components: { HeaderView, SpinnerComponent },

  data() {
    return {
      headerTitle: 'Presentation Templates',
      templates: [],
      isLoading: true,
      isUploading: false,
      selectedFile: null,
      newDescription: '',
      successMsg: '',
      errorMsg: '',
      replaceTargetId: null,
      replacing: false,
      apiUrl: import.meta.env.VITE_API_URL,
    }
  },

  setup() {
    const authStore = useAuthStore()
    const raw = authStore.permissions || []
    const permissionCodes = raw.map(p => (typeof p === 'string' ? p : p.permission_code))
    const isAdmin = permissionCodes.includes('ADMIN_DASHBOARD')
    return { permissionCodes, isAdmin, accessToken: authStore.accessToken }
  },

  mounted() {
    setAuthToken()
    this.loadTemplates()
  },

  methods: {
    async loadTemplates() {
      this.isLoading = true
      try {
        const res = await axios.get(`${this.apiUrl}/presentation_templates`, {
          headers: { Authorization: `Bearer ${this.accessToken}` },
        })
        this.templates = res.data
      } catch (e) {
        this.errorMsg = 'Failed to load templates.'
      } finally {
        this.isLoading = false
      }
    },

    onFileSelected(e) {
      this.selectedFile = e.target.files[0] || null
    },

    async uploadTemplate() {
      if (!this.selectedFile) return
      this.isUploading = true
      this.successMsg = ''
      this.errorMsg = ''
      try {
        const form = new FormData()
        form.append('file', this.selectedFile)
        form.append('description', this.newDescription)
        await axios.post(`${this.apiUrl}/presentation_templates`, form, {
          headers: {
            Authorization: `Bearer ${this.accessToken}`,
            'Content-Type': 'multipart/form-data',
          },
        })
        this.successMsg = 'Template uploaded successfully.'
        this.selectedFile = null
        this.newDescription = ''
        if (this.$refs.fileInput) this.$refs.fileInput.value = ''
        this.loadTemplates()
      } catch (e) {
        this.errorMsg = e.response?.data?.detail || 'Upload failed.'
      } finally {
        this.isUploading = false
      }
    },

    async deleteTemplate(id) {
      if (!confirm('Delete this template?')) return
      try {
        await axios.delete(`${this.apiUrl}/presentation_templates/${id}`, {
          headers: { Authorization: `Bearer ${this.accessToken}` },
        })
        this.templates = this.templates.filter(t => t.id !== id)
        this.successMsg = 'Template deleted.'
      } catch (e) {
        this.errorMsg = 'Delete failed.'
      }
    },

    async replaceTemplate(id) {
      this.replaceTargetId = id
      if (this.$refs.replaceFileInput) this.$refs.replaceFileInput.value = ''
      this.$refs.replaceFileInput.click()
    },

    async onReplaceSelected(e) {
      const file = e.target.files[0]
      if (!file || !this.replaceTargetId) return
      this.replacing = true
      this.successMsg = ''
      this.errorMsg = ''
      try {
        const form = new FormData()
        form.append('file', file)
        const res = await axios.post(`${this.apiUrl}/presentation_templates/${this.replaceTargetId}/replace`, form, {
          headers: {
            Authorization: `Bearer ${this.accessToken}`,
            'Content-Type': 'multipart/form-data',
          },
        })
        const tpl = this.templates.find(t => t.id === this.replaceTargetId)
        if (tpl) {
          tpl.original_name = res.data.original_name
          tpl.file_size = res.data.file_size
        }
        this.successMsg = 'Template file replaced successfully.'
      } catch (e) {
        this.errorMsg = e.response?.data?.detail || 'Replace failed.'
      } finally {
        this.replacing = false
        this.replaceTargetId = null
        if (this.$refs.replaceFileInput) this.$refs.replaceFileInput.value = ''
      }
    },

    formatSize(bytes) {
      if (!bytes) return '—'
      if (bytes < 1024) return `${bytes} B`
      if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
      return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
    },

    fileIcon(name) {
      const ext = (name || '').split('.').pop().toLowerCase()
      const map = { pptx: '📊', ppt: '📊', docx: '📄', doc: '📄', pdf: '📕', zip: '🗜️' }
      return map[ext] || '📎'
    },
  },
}
</script>
