<template>
  <div class="bg-gray-50 text-gray-800 min-h-screen pb-10">
    <div class="px-4 pt-6 pb-4" style="background: linear-gradient(135deg, rgb(254,80,103) 0%, rgb(180,30,55) 100%);">
      <div class="max-w-2xl mx-auto">
        <div v-if="data && data.event" class="text-white/80 text-xs font-semibold mb-1">{{ data.event.name }}</div>
        <h1 class="text-white text-xl font-bold">{{ room }}</h1>
        <p class="text-white/90 text-sm mt-0.5">{{ day }} · running order</p>
      </div>
    </div>

    <div class="max-w-2xl mx-auto px-4 -mt-3">
      <div v-if="loading" class="py-16"><SpinnerComponent /></div>

      <template v-else-if="loadError">
        <div class="bg-white rounded-xl shadow-sm p-6 text-center text-sm text-red-600 mt-3">{{ loadError }}</div>
      </template>

      <template v-else>
        <div class="bg-white rounded-xl shadow-sm p-3 mt-3 flex items-center justify-between">
          <span class="text-xs text-gray-500">
            {{ entries.length }} presentation{{ entries.length === 1 ? '' : 's' }}
            · {{ withSlideCount }} with slides
          </span>
          <button v-if="withSlideCount" @click="downloadAll" :disabled="zipBusy"
            class="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-semibold text-white"
            style="background-color: rgb(0,150,180);">
            <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"/>
            </svg>
            {{ zipBusy ? 'Zipping…' : 'Download all slides' }}
          </button>
        </div>

        <div v-if="entries.length === 0" class="bg-white rounded-xl shadow-sm p-8 text-center text-sm text-gray-400 italic mt-3">
          Nothing scheduled here yet.
        </div>

        <div class="space-y-2 mt-3">
          <div v-for="e in entries" :key="e.id" class="bg-white rounded-xl shadow-sm p-3.5">
            <div class="flex flex-wrap items-center gap-x-2 gap-y-0.5">
              <span class="font-semibold text-sm">{{ e.presenter_name || '—' }}</span>
              <template v-if="e.is_substitution">
                <span class="badge badge-sub">SUB</span>
                <span v-if="e.original_presenter" class="text-xs text-gray-500">for {{ e.original_presenter }}</span>
              </template>
            </div>
            <div class="text-xs text-gray-500 mt-0.5 flex flex-wrap items-center gap-x-2 gap-y-0.5">
              <span v-if="e.code" class="font-mono">{{ e.code }}</span>
              <span v-if="e.session">Session {{ e.session }}</span>
              <span v-if="e.category === 'poster'" class="uppercase tracking-wide text-amber-600">Poster</span>
            </div>
            <div class="text-sm text-gray-700 mt-1">{{ e.title || e.activity || '' }}</div>
            <div class="mt-2 flex items-center gap-2">
              <template v-if="e.has_presentation">
                <button v-if="isPreviewable(e.presentation_ext)" @click="openPreview(e)"
                  class="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-semibold border"
                  style="border-color: rgb(0,150,180); color: rgb(0,150,180);">
                  Preview
                </button>
                <button @click="downloadSingle(e)"
                  class="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-semibold border border-gray-200 text-gray-600">
                  Download
                </button>
              </template>
              <span v-else class="text-xs text-gray-400 italic">no slides yet</span>
            </div>
          </div>
        </div>

        <p class="text-[11px] text-gray-400 text-center mt-6">
          This link always shows the latest schedule for this room — reload any time to check for new slides.
        </p>
      </template>
    </div>

    <!-- Preview modal -->
    <div v-if="preview.open" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60" @click.self="preview.open = false">
      <div class="bg-white rounded-xl shadow-xl w-full max-w-3xl h-[85vh] flex flex-col">
        <div class="px-4 py-3 border-b border-gray-100 flex items-center justify-between">
          <div class="font-semibold text-sm truncate pr-4">{{ preview.name }}</div>
          <button @click="preview.open = false" class="text-gray-400 hover:text-gray-600">
            <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" d="M6 18L18 6M6 6l12 12"/></svg>
          </button>
        </div>
        <div class="flex-1 bg-gray-100 min-h-0">
          <iframe :src="preview.src" class="w-full h-full border-0" title="Slides preview"></iframe>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import SpinnerComponent from '@/components/Spinner.vue'
import { saveAs } from 'file-saver'
import axios from 'axios'

const POLL_MS = 25000

export default {
  name: 'RoomProgrammeView',
  components: { SpinnerComponent },

  data() {
    return {
      apiUrl: import.meta.env.VITE_API_URL,
      eventId: this.$route.query.event_id || 1,
      day: this.$route.query.day || '',
      room: this.$route.query.room || '',
      data: null,
      loading: true,
      loadError: '',
      zipBusy: false,
      preview: { open: false, name: '', src: '' },
      _pollTimer: null,
    }
  },

  computed: {
    entries() {
      return (this.data && this.data.entries) || []
    },
    withSlideCount() {
      return this.entries.filter(e => e.has_presentation).length
    },
  },

  mounted() {
    if (!this.day || !this.room) {
      this.loading = false
      this.loadError = 'This link is missing its room/day — ask the secretariat to re-share it.'
      return
    }
    this.load()
    // Keep it current without the leader having to remember to reload —
    // slides/matches can land after they've already opened the link.
    this._pollTimer = setInterval(() => this.load(true), POLL_MS)
  },
  beforeUnmount() {
    if (this._pollTimer) clearInterval(this._pollTimer)
  },

  methods: {
    async load(silent = false) {
      if (!silent) this.loading = true
      try {
        const res = await axios.get(`${this.apiUrl}/programme/room-view`, {
          params: { event_id: this.eventId, day: this.day, room: this.room },
        })
        this.data = res.data
        this.loadError = ''
      } catch (e) {
        if (!silent) this.loadError = e.response?.data?.detail || 'Failed to load this room.'
      } finally {
        this.loading = false
      }
    },
    isPreviewable(ext) {
      const e = (ext || '').replace(/^\./, '').toLowerCase()
      return ['pdf', 'jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp'].includes(e)
    },
    openPreview(entry) {
      const fileUrl = `${this.apiUrl}/programme/${entry.id}/preview-presentation`
      this.preview = { open: true, name: entry.title || entry.presenter_name, src: fileUrl }
    },
    async downloadSingle(entry) {
      try {
        const res = await axios.get(`${this.apiUrl}/programme/${entry.id}/download-presentation`, {
          responseType: 'blob',
        })
        const ext = (entry.presentation_ext || '').replace(/^\./, '')
        const clean = (entry.code || entry.presenter_name || 'presentation').replace(/[^A-Za-z0-9 _-]+/g, '').trim().slice(0, 60)
        saveAs(res.data, `${clean || 'presentation'}.${ext}`)
      } catch (e) {
        this.loadError = 'Download failed.'
      }
    },
    async downloadAll() {
      this.zipBusy = true
      try {
        const res = await axios.get(`${this.apiUrl}/programme/download-room-zip`, {
          params: { event_id: this.eventId, room: this.room, day: this.day },
          responseType: 'blob',
        })
        saveAs(res.data, `${(this.room || 'room').replace(/[^A-Za-z0-9_]+/g, '_')}_slides.zip`)
      } catch (e) {
        this.loadError = 'No slides to download for this room yet.'
      } finally {
        this.zipBusy = false
      }
    },
  },
}
</script>

<style scoped>
.badge {
  @apply inline-flex items-center px-2 py-0.5 rounded text-[11px] font-semibold;
}
.badge-sub { @apply badge bg-purple-100 text-purple-700; }
</style>
