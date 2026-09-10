<template>
  <div v-if="show" class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
    <div class="bg-white rounded-2xl shadow-xl w-full max-w-4xl h-[90vh] flex flex-col overflow-hidden">
      <div class="flex items-center justify-between px-5 py-3 border-b border-gray-100 flex-shrink-0">
        <h3 class="font-bold text-gray-800 truncate pr-4">{{ title }}</h3>
        <div class="flex items-center gap-2 flex-shrink-0">
          <button @click="download" :disabled="!blobUrl"
            class="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold border-2 transition disabled:opacity-40"
            style="border-color: rgb(254,80,103); color: rgb(254,80,103);">
            <ArrowDownTrayIcon class="w-4 h-4" />
            Download
          </button>
          <button @click="close" class="text-gray-400 hover:text-gray-600 transition p-1">
            <svg class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
      </div>

      <div class="flex-1 min-h-0 relative">
        <div v-if="loading" class="absolute inset-0 flex items-center justify-center">
          <svg class="animate-spin w-8 h-8" style="color: rgb(254,80,103);" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"/>
          </svg>
        </div>
        <div v-else-if="error" class="absolute inset-0 flex items-center justify-center p-6 text-center">
          <p class="text-sm text-red-600">{{ error }}</p>
        </div>
        <iframe v-else-if="blobUrl" :src="blobUrl" class="w-full h-full" style="border:none;"></iframe>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'
import { useAuthStore } from '@/store/authStore'
import { ArrowDownTrayIcon } from '@heroicons/vue/24/solid'

const API_URL = import.meta.env.VITE_API_URL

export default {
  name: 'PdfPreviewModal',
  components: { ArrowDownTrayIcon },
  props: {
    show: { type: Boolean, default: false },
    title: { type: String, default: 'Preview' },
    // API path (relative to VITE_API_URL) returning the PDF, e.g. '/abstracts/abstract-book?event_id=1'
    fetchUrl: { type: String, default: '' },
    filename: { type: String, default: 'document.pdf' },
  },
  data() {
    return { loading: false, error: '', blobUrl: '', authStore: useAuthStore() }
  },
  watch: {
    show(val) {
      if (val) this.load()
      else this.revoke()
    },
    fetchUrl() {
      if (this.show) this.load()
    },
  },
  beforeUnmount() {
    this.revoke()
  },
  methods: {
    revoke() {
      if (this.blobUrl) { window.URL.revokeObjectURL(this.blobUrl); this.blobUrl = '' }
    },
    async load() {
      if (!this.fetchUrl) return
      this.revoke()
      this.loading = true
      this.error = ''
      try {
        const api = axios.create({ baseURL: API_URL })
        const token = this.authStore.accessToken
        if (token) api.defaults.headers.common['Authorization'] = `Bearer ${token}`
        const res = await api.get(this.fetchUrl, { responseType: 'blob' })
        this.blobUrl = window.URL.createObjectURL(res.data)
      } catch (e) {
        this.error = e.response?.data?.detail || 'Failed to load preview.'
      } finally {
        this.loading = false
      }
    },
    download() {
      if (!this.blobUrl) return
      const a = document.createElement('a')
      a.href = this.blobUrl
      a.download = this.filename
      document.body.appendChild(a)
      a.click()
      a.remove()
    },
    close() {
      this.$emit('update:show', false)
      this.$emit('close')
    },
  },
}
</script>
