<template>
  <div class="bg-gray-50 text-gray-800 min-h-screen pb-10">
    <div class="px-4 pt-6 pb-4" style="background: linear-gradient(135deg, rgb(254,80,103) 0%, rgb(180,30,55) 100%);">
      <div class="max-w-5xl mx-auto">
        <div v-if="eventName" class="text-white/80 text-xs font-semibold mb-1">{{ eventName }}</div>
        <h1 class="text-white text-xl font-bold">Conference Programme — by Room</h1>
        <p class="text-white/90 text-sm mt-0.5">Presenters, sessions and slides for every room — reload any time for the latest schedule.</p>
      </div>
    </div>

    <div class="max-w-5xl mx-auto px-4 -mt-3">
      <div v-if="loading" class="py-16"><SpinnerComponent /></div>

      <template v-else-if="loadError">
        <div class="bg-white rounded-xl shadow-sm p-6 text-center text-sm text-red-600 mt-3">{{ loadError }}</div>
      </template>

      <template v-else>
        <!-- Controls -->
        <div class="bg-white rounded-xl shadow-sm p-3 mt-3 space-y-2.5">
          <div class="flex items-center gap-2">
            <button v-for="c in categoryOptions" :key="c.key" type="button" @click="entryCategory = c.key"
              class="px-3 py-1.5 rounded-full text-xs font-semibold transition"
              :class="entryCategory === c.key ? 'text-white' : 'bg-gray-50 text-gray-600 hover:bg-gray-100'"
              :style="entryCategory === c.key ? { backgroundColor: 'rgb(254,80,103)' } : {}">
              {{ c.label }}
            </button>
          </div>
          <div class="flex flex-wrap items-center gap-2">
            <button v-for="d in dayFilterChips" :key="d" type="button" @click="activeDay = d"
              class="px-3 py-1.5 rounded-full text-xs font-semibold transition"
              :class="activeDay === d ? 'text-white' : 'bg-gray-50 text-gray-600 hover:bg-gray-100'"
              :style="activeDay === d ? { backgroundColor: 'rgb(0,150,180)' } : {}">
              {{ d }}
            </button>
            <button v-if="pastDaysCount > 0" type="button" @click="showPastDays = !showPastDays"
              class="text-xs font-semibold hover:underline" style="color: rgb(0,150,180);">
              {{ showPastDays ? 'Hide past days' : `Show ${pastDaysCount} past day${pastDaysCount !== 1 ? 's' : ''}` }}
            </button>
          </div>
          <div class="flex flex-wrap items-center gap-2">
            <button v-for="r in roomFilterChips" :key="r" type="button" @click="activeRoom = r"
              class="px-3 py-1.5 rounded-full text-xs font-semibold transition"
              :class="activeRoom === r ? 'text-white' : 'bg-gray-50 text-gray-600 hover:bg-gray-100'"
              :style="activeRoom === r ? { backgroundColor: 'rgb(0,150,180)' } : {}">
              {{ r }}
            </button>
          </div>
        </div>

        <div v-if="!roomDays.length" class="bg-white rounded-xl shadow-sm p-8 text-center text-sm text-gray-400 italic mt-3">
          Nothing scheduled yet.
        </div>

        <div class="space-y-5 mt-3">
          <div v-for="day in roomDays" :key="day.day" class="space-y-3">
            <div class="flex items-center gap-2">
              <div class="px-3 py-1 rounded-full text-xs font-bold text-white" style="background-color: rgb(254,80,103);">{{ day.day }}</div>
              <div class="text-xs text-gray-500">{{ day.rooms.length }} room{{ day.rooms.length !== 1 ? 's' : '' }} · {{ day.total }} presentations</div>
            </div>

            <div class="grid grid-cols-1 lg:grid-cols-2 gap-4">
              <div v-for="room in day.rooms" :key="room.day + room.room"
                class="rounded-xl border border-gray-100 bg-white overflow-hidden shadow-sm">
                <div class="px-4 py-3 flex items-center justify-between" style="background-color: rgb(0,150,180);">
                  <div class="font-bold text-white flex items-center gap-2">
                    <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.75">
                      <path stroke-linecap="round" stroke-linejoin="round" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"/><path stroke-linecap="round" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"/>
                    </svg>
                    {{ room.room }}
                  </div>
                  <div class="flex items-center gap-2">
                    <span class="text-[11px] text-white/90 font-medium">{{ room.total }}</span>
                    <button v-if="room.with_slide" type="button" @click="downloadRoomZip(room)" :disabled="zipBusy"
                      class="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-[11px] font-semibold bg-white hover:opacity-90 disabled:opacity-50"
                      style="color: rgb(0,150,180);">
                      <svg class="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                        <path stroke-linecap="round" stroke-linejoin="round" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"/>
                      </svg>
                      All slides
                    </button>
                  </div>
                </div>
                <div class="divide-y divide-gray-50">
                  <div v-if="room.entries.length === 0" class="px-4 py-6 text-center text-sm text-gray-400 italic">
                    No presentations scheduled.
                  </div>
                  <div v-for="e in room.entries" :key="e.id" class="px-4 py-3 flex items-start gap-3">
                    <div class="flex-1 min-w-0">
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
                        <span v-if="e.category === 'plenary' && e.role" class="italic">{{ e.role }}</span>
                      </div>
                      <div class="text-sm text-gray-700 mt-1">{{ e.title || e.activity || '' }}</div>
                    </div>
                    <div class="flex items-center gap-1 flex-shrink-0">
                      <template v-if="e.has_presentation">
                        <button v-if="isPreviewable(e.presentation_ext)" type="button" @click="openPreview(e)"
                          class="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-semibold border"
                          style="border-color: rgb(0,150,180); color: rgb(0,150,180);">
                          Preview
                        </button>
                        <button type="button" @click="downloadSingle(e)"
                          class="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-semibold border border-gray-200 text-gray-600">
                          Download
                        </button>
                      </template>
                      <a v-if="e.video_url" :href="e.video_url" target="_blank" rel="noopener"
                        class="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-semibold border"
                        style="border-color: rgb(120,80,200); color: rgb(100,60,180);">
                        Watch video
                      </a>
                      <span v-if="!e.has_presentation && !e.video_url" class="text-xs text-gray-400 italic">no slides yet</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <p class="text-[11px] text-gray-400 text-center mt-6">
          This page always shows the latest schedule — reload any time to check for new slides.
        </p>
      </template>
    </div>

    <!-- Preview modal -->
    <div v-if="preview.open" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60" @click.self="preview.open = false">
      <div class="bg-white rounded-xl shadow-xl w-full max-w-3xl h-[85vh] flex flex-col">
        <div class="px-4 py-3 border-b border-gray-100 flex items-center justify-between">
          <div class="font-semibold text-sm truncate pr-4">{{ preview.name }}</div>
          <button type="button" @click="preview.open = false" class="text-gray-400 hover:text-gray-600">
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

const DAY_ORDER = ['Day 1', 'Day 2', 'Day 3', 'Day 1-3', 'Unassigned']

export default {
  name: 'PublicProgrammeRoomsView',
  components: { SpinnerComponent },

  data() {
    return {
      apiUrl: import.meta.env.VITE_API_URL,
      eventId: this.$route.query.event_id || 1,
      eventName: '',
      eventStartDate: null,
      eventEndDate: null,
      roomsData: [],
      loading: true,
      loadError: '',
      activeRoom: 'All Rooms',
      activeDay: 'Day 1',
      showPastDays: false,
      entryCategory: 'oral',
      categoryOptions: [
        { key: 'oral', label: 'Abstracts' },
        { key: 'poster', label: 'Posters' },
        { key: 'plenary', label: 'Plenary' },
      ],
      zipBusy: false,
      preview: { open: false, name: '', src: '' },
    }
  },

  computed: {
    categoryRoomsData() {
      return this.roomsData
        .map(d => {
          const entries = d.entries.filter(e => e.category === this.entryCategory)
          return {
            ...d,
            entries,
            total: entries.length,
            with_slide: entries.filter(e => e.has_presentation).length,
          }
        })
        .filter(d => d.entries.length > 0)
    },
    roomFilterChips() {
      const rooms = new Set(['All Rooms'])
      for (const d of this.categoryRoomsData) {
        for (const r of d.entries) {
          if (r.room) rooms.add(r.room)
        }
      }
      const all = [...rooms]
      return all.sort((a, b) => (a === 'All Rooms' ? -1 : b === 'All Rooms' ? 1 : a.localeCompare(b)))
    },
    allRoomDays() {
      const grouped = {}
      for (const d of this.categoryRoomsData) {
        if (this.activeRoom !== 'All Rooms' && d.room !== this.activeRoom) continue
        ;(grouped[d.day] = grouped[d.day] || []).push(d)
      }
      return DAY_ORDER.filter(day => grouped[day]).map(day => ({
        day,
        rooms: grouped[day],
        total: grouped[day].reduce((s, r) => s + r.total, 0),
        isPast: this.isDayPast(day),
      }))
    },
    allDaysGlobal() {
      const grouped = {}
      for (const d of this.categoryRoomsData) {
        ;(grouped[d.day] = grouped[d.day] || []).push(d)
      }
      return DAY_ORDER.filter(day => grouped[day]).map(day => ({
        day,
        isPast: this.isDayPast(day),
      }))
    },
    pastDaysCount() {
      return this.allDaysGlobal.filter(d => d.isPast).length
    },
    dayFilterChips() {
      const days = this.allDaysGlobal.filter(d => this.showPastDays || !d.isPast)
      return ['All Days', ...days.map(d => d.day)]
    },
    roomDays() {
      return this.allRoomDays.filter(d => {
        if (!this.showPastDays && d.isPast) return false
        if (this.activeDay !== 'All Days' && d.day !== this.activeDay) return false
        return true
      })
    },
  },

  watch: {
    entryCategory() {
      this.activeRoom = 'All Rooms'
      this.activeDay = 'All Days'
    },
  },

  mounted() {
    this.load()
  },

  methods: {
    // "Day N" labels map to event_start_date + (N-1) days, same convention
    // as the admin Rooms page — used only to default-hide days already past.
    isDayPast(day) {
      const m = /^Day (\d+)$/.exec(day)
      if (!m || !this.eventStartDate) return false
      const start = new Date(this.eventStartDate + 'T00:00:00')
      const dayDate = new Date(start.getTime() + (parseInt(m[1], 10) - 1) * 86400000)
      const today = new Date(); today.setHours(0, 0, 0, 0)
      return dayDate < today
    },
    async load() {
      this.loading = true
      try {
        const res = await axios.get(`${this.apiUrl}/programme/public-rooms`, {
          params: { event_id: this.eventId },
        })
        this.roomsData = res.data.data || []
        this.eventName = res.data.event?.name || ''
        this.eventStartDate = res.data.event_start_date || null
        this.eventEndDate = res.data.event_end_date || null
        this.loadError = ''
        // Defaults to Day 1, but if the conference has already happened,
        // Day 1 is a "past day" and hidden by default — without this it'd
        // silently render an empty page instead of showing anything.
        if (this.activeDay === 'Day 1' && this.isDayPast('Day 1')) {
          this.showPastDays = true
        }
      } catch (e) {
        this.loadError = e.response?.data?.detail || 'Failed to load the programme.'
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
    async downloadRoomZip(room) {
      this.zipBusy = true
      try {
        const res = await axios.get(`${this.apiUrl}/programme/download-room-zip`, {
          params: { event_id: this.eventId, room: room.room, day: room.day },
          responseType: 'blob',
        })
        saveAs(res.data, `${(room.room || 'room').replace(/[^A-Za-z0-9_]+/g, '_')}_slides.zip`)
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
