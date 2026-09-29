<template>
  <div class="min-h-screen bg-gray-50 text-gray-800">
    <!-- ── Hero ─────────────────────────────────────────────────────────── -->
    <div class="relative overflow-hidden px-4 pt-7 pb-16"
      style="background: linear-gradient(135deg, rgb(254,80,103) 0%, rgb(180,30,55) 100%);">
      <div class="absolute inset-0 pointer-events-none"
        style="background-image: radial-gradient(circle at 16% 10%, rgba(255,255,255,.5) 0, transparent 42%), radial-gradient(circle at 84% 2%, rgba(255,255,255,.3) 0, transparent 38%);" />
      <div class="relative max-w-6xl mx-auto">
        <div v-if="eventName" class="text-white/85 text-[11px] font-semibold uppercase tracking-wider">
          {{ eventName }}
        </div>
        <h1 class="text-white text-2xl sm:text-3xl font-bold mt-1">Conference presentations</h1>
        <p class="text-white/90 text-sm mt-1.5 max-w-2xl">
          Find a session by day and room, or search a presenter or title. Every entry links straight
          to that presenter's own slides or poster file.
        </p>
        <div v-if="dateRange"
          class="mt-3.5 inline-flex items-center gap-1.5 rounded-full bg-white/20 px-3 py-1 text-white text-xs font-semibold">
          <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round"
              d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 0z" />
          </svg>
          {{ dateRange }}
        </div>
      </div>
    </div>

    <!-- ── Control bar ───────────────────────────────────────────────────── -->
    <div class="max-w-6xl mx-auto px-4 -mt-9 relative z-20">
      <div class="bg-white rounded-2xl shadow-lg shadow-black/5 border border-gray-100 p-3 sm:p-4">

        <div class="flex flex-col lg:flex-row lg:items-center gap-3">
          <!-- category segmented control -->
          <div class="flex flex-wrap items-center gap-1.5 self-start">
            <button v-for="c in categoryOptions" :key="c.key" type="button" @click="entryCategory = c.key"
              class="px-3 py-1.5 rounded-full text-xs font-semibold transition border whitespace-nowrap"
              :class="entryCategory === c.key
                ? 'bg-gray-900 text-white border-gray-900'
                : 'bg-white text-gray-600 border-gray-200 hover:border-gray-400'">
              {{ c.label }}
              <span class="ml-1 tabular-nums opacity-55">{{ categoryCounts[c.key] }}</span>
            </button>
          </div>

          <!-- search -->
          <div class="relative flex-1 min-w-0">
            <svg class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400 pointer-events-none"
              fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round"
                d="M21 21l-4.35-4.35M17 11a6 6 0 11-12 0 6 6 0 0112 0z" />
            </svg>
            <input ref="searchInput" v-model="query" type="search" placeholder="Search presenter, title, code…"
              class="w-full pl-9 pr-9 py-2 rounded-xl bg-gray-50 border border-gray-200 text-sm outline-none focus:border-gray-400 focus:bg-white focus:ring-2 focus:ring-gray-900/5 transition" />
            <button v-if="query" type="button" @click="query = ''"
              class="absolute right-2.5 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
              title="Clear search">
              <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                <path stroke-linecap="round" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>

        <!-- day chips + room select -->
        <div class="flex flex-wrap items-center gap-x-4 gap-y-2.5 mt-3 pt-3 border-t border-gray-100">
          <div class="flex flex-wrap items-center gap-1.5" :class="query ? 'opacity-40 pointer-events-none' : ''">
            <button v-for="d in dayFilterChips" :key="d" type="button" @click="activeDay = d" :disabled="!!query"
              class="px-3 py-1.5 rounded-full text-xs font-semibold transition border disabled:cursor-not-allowed"
              :class="activeDay === d
                ? 'bg-gray-900 text-white border-gray-900'
                : 'bg-white text-gray-600 border-gray-200 hover:border-gray-400'">
              {{ d }}
              <!-- counts are per-category while browsing; during a search the
                   pool widens to every category, so they'd be misleading -->
              <span v-if="d !== 'All Days' && !query" class="ml-1 tabular-nums opacity-55">{{ dayCounts[d] }}</span>
            </button>
            <button v-if="pastDaysCount > 0 && !query" type="button" @click="showPastDays = !showPastDays"
              class="text-xs font-semibold text-gray-500 hover:text-gray-800 underline underline-offset-2 decoration-dotted">
              {{ showPastDays ? 'Hide past days' : `Show ${pastDaysCount} past day${pastDaysCount !== 1 ? 's' : ''}` }}
            </button>
          </div>

          <div class="flex items-center gap-2" :class="query ? 'opacity-40 pointer-events-none' : ''">
            <label for="room-select" class="text-xs font-semibold text-gray-500">Room</label>
            <select id="room-select" v-model="activeRoom" :disabled="!!query"
              class="text-xs font-semibold text-gray-700 bg-white border border-gray-200 rounded-lg px-2.5 py-1.5 outline-none focus:border-gray-400 disabled:cursor-not-allowed">
              <option v-for="r in roomFilterChips" :key="r" :value="r">{{ r }}</option>
            </select>
          </div>

          <button v-if="hasNonDefaultFilters" type="button" @click="resetFilters"
            class="text-xs font-semibold text-gray-500 hover:text-gray-900 underline underline-offset-2 decoration-dotted ml-auto">
            Reset filters
          </button>
        </div>

        <!-- result summary -->
        <p class="mt-3 text-xs text-gray-500">
          <template v-if="query">
            <span class="font-semibold text-gray-800">{{ totalShown }}</span> match{{ totalShown !== 1 ? 'es' : '' }}
            for “{{ query }}” across all days, rooms and categories
          </template>
          <template v-else>
            <span class="font-semibold text-gray-800">{{ totalShown }}</span>
            {{ totalShown === 1 ? visibleNoun.one : visibleNoun.many }}
            in {{ roomDays.length }} day{{ roomDays.length !== 1 ? 's' : '' }}
            <template v-if="activeRoom !== 'All Rooms'"> · {{ activeRoom }}</template>
            <span v-if="hiddenPastCount" class="text-amber-600">
              · {{ hiddenPastCount }} past day{{ hiddenPastCount !== 1 ? 's are' : ' is' }} hidden
            </span>
          </template>
        </p>
      </div>
    </div>

    <!-- ── Body ─────────────────────────────────────────────────────────── -->
    <div class="max-w-6xl mx-auto px-4">
      <div v-if="loading" class="py-16"><SpinnerComponent /></div>

      <div v-else-if="loadError"
        class="bg-white rounded-2xl border border-red-100 shadow-sm p-6 text-center text-sm text-red-600 mt-4">
        {{ loadError }}
      </div>

      <template v-else>
        <!-- nothing scheduled at all in this category -->
        <div v-if="!query && !totalInCategory"
          class="bg-white rounded-2xl border border-gray-100 shadow-sm p-10 text-center mt-4">
          <div class="text-sm font-semibold text-gray-700">Nothing scheduled yet</div>
          <p class="text-xs text-gray-400 mt-1">Presentations will appear here as the secretariat publishes them.</p>
        </div>

        <!-- filters/search match nothing -->
        <div v-else-if="!roomDays.length"
          class="bg-white rounded-2xl border border-gray-100 shadow-sm p-10 text-center mt-4">
          <div class="text-sm font-semibold text-gray-700">
            <template v-if="query">No matches for “{{ query }}”</template>
            <template v-else>No {{ activeCategoryLabel.toLowerCase() }} on this day</template>
          </div>
          <p class="text-xs text-gray-400 mt-1">
            <template v-if="query">Try a shorter name, or a different day or room.</template>
            <template v-else>Try another day, room, or category above.</template>
          </p>
          <button v-if="hasNonDefaultFilters" type="button" @click="resetFilters"
            class="mt-4 px-3.5 py-1.5 rounded-lg text-xs font-semibold bg-gray-900 text-white hover:bg-gray-700">
            Reset filters
          </button>
        </div>

        <div v-else class="space-y-8 mt-5 pb-4">
          <section v-for="day in roomDays" :key="day.day">
            <!-- day heading -->
            <div class="sticky top-0 z-10 -mx-1 px-1 py-2 mb-3 bg-gray-50/85 backdrop-blur-sm">
              <div class="flex items-baseline gap-2.5">
                <h2 class="text-sm font-bold text-gray-900">{{ day.day }}</h2>
                <span class="text-xs text-gray-500 tabular-nums">
                  {{ day.rooms.length }} room{{ day.rooms.length !== 1 ? 's' : '' }} ·
                  {{ day.total }} {{ day.total === 1 ? visibleNoun.one : visibleNoun.many }}
                </span>
                <span v-if="day.isPast" class="text-[10px] font-semibold uppercase tracking-wide text-gray-400 border border-gray-200 rounded px-1.5 py-0.5">
                  Past
                </span>
              </div>
            </div>

            <div class="grid grid-cols-1 lg:grid-cols-2 gap-4">
              <!-- per room -->
              <div v-for="room in day.rooms" :key="room.day + room.room"
                class="rounded-2xl border border-gray-200/70 bg-white overflow-hidden shadow-sm flex flex-col">

                <div class="px-4 py-2.5 flex items-center justify-between gap-2 border-b border-gray-100"
                  style="background-color: rgb(0,150,180);">
                  <div class="font-bold text-white text-sm flex items-center gap-2 min-w-0">
                    <svg class="w-4 h-4 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.75">
                      <path stroke-linecap="round" stroke-linejoin="round"
                        d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                      <path stroke-linecap="round" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                    </svg>
                    <span class="truncate">{{ room.room }}</span>
                  </div>
                  <div class="flex items-center gap-2 flex-shrink-0">
                    <span class="text-[11px] text-white/85 font-medium tabular-nums" :title="`${room.total} entries, ${room.with_slide} with a file`">
                      {{ room.total }}<span class="opacity-60"> · </span>{{ room.with_slide }} file{{ room.with_slide !== 1 ? 's' : '' }}
                    </span>
                    <button v-if="room.with_slide" type="button" @click="downloadRoomZip(room)" :disabled="zipBusy"
                      title="Download every uploaded file in this room as a ZIP"
                      class="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-[11px] font-semibold bg-white hover:opacity-90 disabled:opacity-50"
                      style="color: rgb(0,150,180);">
                      <svg class="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                        <path stroke-linecap="round" stroke-linejoin="round"
                          d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                      </svg>
                      All
                    </button>
                  </div>
                </div>

                <!-- entries — no session grouping, slides-first order -->
                <div class="flex-1">
                  <div class="divide-y divide-gray-50">
                    <div v-for="e in room.entries" :key="e.id"
                      class="px-4 py-3 flex items-start gap-3 hover:bg-gray-50/70 transition-colors">

                      <!-- slide / file availability dot -->
                      <span class="mt-[7px] w-1.5 h-1.5 rounded-full flex-shrink-0"
                        :class="e.has_presentation ? 'bg-emerald-500' : 'bg-gray-200'"
                        :title="e.has_presentation ? 'File uploaded' : 'No file uploaded yet'" />

                      <div class="flex-1 min-w-0">
                        <!-- title first: that's what people scan for -->
                        <div class="text-[15px] font-medium leading-snug text-gray-900">
                          <template v-for="(seg, i) in splitHighlight(e.title || e.activity || '')" :key="i">
                            <mark v-if="seg.hit" class="bg-yellow-200 text-gray-900 rounded-sm px-0.5">{{ seg.t }}</mark>
                            <template v-else>{{ seg.t }}</template>
                          </template>
                        </div>

                        <div class="mt-1 flex flex-wrap items-center gap-x-2 gap-y-1">
                          <span class="text-sm text-gray-600">
                            <template v-for="(seg, i) in splitHighlight(e.presenter_name || '—')" :key="i">
                              <mark v-if="seg.hit" class="bg-yellow-200 text-gray-900 rounded-sm px-0.5">{{ seg.t }}</mark>
                              <template v-else>{{ seg.t }}</template>
                            </template>
                          </span>
                          <span v-if="e.code"
                            class="text-[10px] font-mono font-semibold text-gray-500 bg-gray-100 rounded px-1.5 py-0.5">
                            {{ e.code }}
                          </span>
                          <span v-if="e.is_substitution" class="badge-sub"
                            :title="e.original_presenter ? `Replacing ${e.original_presenter}` : 'Substitution'">
                            SUB
                          </span>
                          <span v-if="e.original_presenter && e.is_substitution" class="text-xs text-gray-400">
                            for {{ e.original_presenter }}
                          </span>
                          <span v-if="e.category === 'plenary' && e.role" class="text-xs italic text-gray-500">{{ e.role }}</span>
                        </div>
                      </div>

                      <!-- actions -->
                      <div class="flex items-center gap-1 flex-shrink-0 flex-wrap justify-end">
                        <template v-if="e.has_presentation">
                          <button v-if="isPreviewable(e.presentation_ext)" type="button" @click="openPreview(e)"
                            title="Open in a new preview window"
                            class="act act-preview">
                            <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                              <path stroke-linecap="round" stroke-linejoin="round"
                                d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                              <path stroke-linecap="round" stroke-linejoin="round"
                                d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                            </svg>
                            <span class="hidden sm:inline">Preview</span>
                          </button>
                          <button type="button" @click="downloadSingle(e)" title="Download this file"
                            class="act act-download">
                            <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                              <path stroke-linecap="round" stroke-linejoin="round"
                                d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                            </svg>
                            <span class="hidden sm:inline">Download</span>
                          </button>
                        </template>
                        <a v-if="e.video_url" :href="e.video_url" target="_blank" rel="noopener" title="Watch the recording"
                          class="act act-video">
                          <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                            <path stroke-linecap="round" stroke-linejoin="round"
                              d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
                          </svg>
                          <span class="hidden sm:inline">Watch</span>
                        </a>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </section>
        </div>

        <!-- legend -->
        <div v-if="totalShown" class="mt-6 flex flex-wrap items-center justify-center gap-x-5 gap-y-1.5 text-[11px] text-gray-400">
          <span class="inline-flex items-center gap-1.5">
            <span class="w-1.5 h-1.5 rounded-full bg-emerald-500" /> file uploaded
          </span>
          <span class="inline-flex items-center gap-1.5">
            <span class="w-1.5 h-1.5 rounded-full bg-gray-200" /> not uploaded yet
          </span>
          <span>Tip: press <kbd class="px-1 rounded border border-gray-200 bg-white">/</kbd> to search</span>
          <span>Press <kbd class="px-1 rounded border border-gray-200 bg-white">Esc</kbd> to clear</span>
        </div>

        <p class="text-[11px] text-gray-400 text-center mt-3 pb-8">
          This page always shows the latest schedule — reload any time to check for new uploads.
        </p>
      </template>
    </div>

    <!-- back to top -->
    <button v-if="showTopButton" type="button" @click="scrollToTop" title="Back to top"
      class="fixed bottom-5 right-5 z-30 w-10 h-10 rounded-full bg-white border border-gray-200 shadow-lg text-gray-600 hover:text-gray-900 hover:border-gray-400 transition flex items-center justify-center">
      <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.25">
        <path stroke-linecap="round" stroke-linejoin="round" d="M5 15l7-7 7 7" />
      </svg>
    </button>

    <!-- ── Preview modal ────────────────────────────────────────────────── -->
    <div v-if="preview.open" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70"
      @click.self="preview.open = false">
      <div class="bg-white rounded-2xl shadow-2xl w-full max-w-4xl h-[88vh] flex flex-col overflow-hidden">
        <div class="px-5 py-3 border-b border-gray-100 flex items-start justify-between gap-4">
          <div class="min-w-0">
            <div class="font-semibold text-sm truncate">{{ preview.name }}</div>
            <div class="text-[11px] text-gray-400 mt-0.5">Uploaded by the presenter — this is their file as submitted.</div>
          </div>
          <button type="button" @click="preview.open = false" title="Close"
            class="text-gray-400 hover:text-gray-600 flex-shrink-0">
            <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        <div class="flex-1 bg-gray-100 min-h-0">
          <iframe :src="preview.src" class="w-full h-full border-0" title="Slides preview"></iframe>
        </div>
      </div>
    </div>

    <!-- Single-file download progress -->
    <div v-if="downloadProgress.active" class="fixed inset-0 z-[70] flex items-center justify-center bg-black/50 p-4">
      <div class="bg-white rounded-2xl shadow-xl w-full max-w-md p-6">
        <div class="flex items-center gap-3 mb-4">
          <svg class="animate-spin w-6 h-6 flex-shrink-0" style="color: rgb(254,80,103);" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"/>
          </svg>
          <div class="min-w-0">
            <p class="text-sm font-bold text-gray-800 truncate">Downloading presentation</p>
            <p class="text-xs text-gray-500">
              {{ downloadProgress.totalMB ? `${downloadProgress.loadedMB} MB of ${downloadProgress.totalMB} MB` : `${downloadProgress.loadedMB} MB downloaded…` }}
            </p>
          </div>
        </div>
        <div v-if="downloadProgress.totalMB" class="h-2 w-full bg-gray-100 rounded-full overflow-hidden">
          <div class="h-full rounded-full transition-all duration-300"
            :style="{ width: downloadProgress.percent + '%', backgroundColor: 'rgb(254,80,103)' }"></div>
        </div>
        <p v-if="downloadProgress.totalMB" class="text-right text-xs text-gray-400 mt-1">{{ downloadProgress.percent }}%</p>
      </div>
    </div>

    <!-- Room ZIP download progress -->
    <div v-if="zipProgress.active" class="fixed inset-0 z-[70] flex items-center justify-center bg-black/50 p-4">
      <div class="bg-white rounded-2xl shadow-xl w-full max-w-md p-6">
        <div class="flex items-center gap-3 mb-4">
          <svg class="animate-spin w-6 h-6 flex-shrink-0" style="color: rgb(254,80,103);" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"/>
          </svg>
          <div class="min-w-0">
            <p class="text-sm font-bold text-gray-800 truncate">Downloading slides — {{ zipProgress.room }}</p>
            <p class="text-xs text-gray-500">
              {{ zipProgress.totalMB ? `${zipProgress.loadedMB} MB of ${zipProgress.totalMB} MB` : `${zipProgress.loadedMB} MB downloaded…` }}
            </p>
          </div>
        </div>
        <div v-if="zipProgress.totalMB" class="h-2 w-full bg-gray-100 rounded-full overflow-hidden">
          <div class="h-full rounded-full transition-all duration-300"
            :style="{ width: zipProgress.percent + '%', backgroundColor: 'rgb(254,80,103)' }"></div>
        </div>
        <p v-if="zipProgress.totalMB" class="text-right text-xs text-gray-400 mt-1">{{ zipProgress.percent }}%</p>
      </div>
    </div>

    <!-- transient unsupported-preview notice -->
    <div v-if="downloadFlash" class="fixed bottom-6 left-1/2 -translate-x-1/2 z-[80] rounded-xl bg-gray-900 text-white text-xs font-medium px-4 py-2.5 shadow-lg">
      {{ downloadFlash }}
    </div>
  </div>
</template>

<script>
import SpinnerComponent from '@/components/Spinner.vue'
import { saveAs } from 'file-saver'
import axios from 'axios'

const DAY_ORDER = ['Day 1', 'Day 2', 'Day 3', 'Day 1-3', 'Unassigned']
const ALL_ROOMS = 'All Rooms'
const ALL_DAYS = 'All Days'

// Count nouns per category tab, so "1 plenary" never reads "1 plenaries".
const CATEGORY_NOUN = {
  oral: { one: 'presentation', many: 'presentations' },
  plenary: { one: 'plenary', many: 'plenaries' },
}

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
      activeRoom: ALL_ROOMS,
      activeDay: ALL_DAYS,
      showPastDays: false,
      query: '',
      entryCategory: 'oral',
      categoryOptions: [
        { key: 'oral', label: 'Abstracts' },
        { key: 'plenary', label: 'Plenary' },
      ],
      zipBusy: false,
      preview: { open: false, name: '', src: '' },
      showTopButton: false,
      // Download progress overlays — the single-file download and the room
      // ZIP each get their own, driven by axios onDownloadProgress (which
      // reports real percentages only when the server sends Content-Length).
      downloadProgress: { active: false, label: '', percent: 0, loadedMB: '0.0', totalMB: null },
      zipProgress: { active: false, room: '', percent: 0, loadedMB: '0.0', totalMB: null },
      downloadFlash: '',
    }
  },

  computed: {
    activeCategoryLabel() {
      return this.categoryOptions.find(c => c.key === this.entryCategory)?.label || ''
    },

    // Noun for whatever is currently visible. A search spans every category,
    // so fall back to the neutral "presentation" rather than the active tab.
    visibleNoun() {
      if (this.query.trim()) return { one: 'presentation', many: 'presentations' }
      return CATEGORY_NOUN[this.entryCategory] || CATEGORY_NOUN.oral
    },

    // Buckets of the active category, each carrying its own entry list.
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

    // Total in the active category before day/room/search filtering.
    totalInCategory() {
      return this.categoryRoomsData.reduce((s, d) => s + d.total, 0)
    },

    categoryCounts() {
      const out = { oral: 0, plenary: 0 }
      for (const d of this.roomsData) {
        for (const e of d.entries) if (out[e.category] !== undefined) out[e.category] += 1
      }
      return out
    },

// The pool the day/room chips and the visible tree are built from. A search
    // deliberately widens to every category: someone looking for a presenter
    // by name shouldn't have to know our taxonomy files them under "Poster".
    // Posters are excluded entirely — the category was removed from this page.
    universeRoomsData() {
      if (!this.query.trim()) return this.categoryRoomsData
      return this.roomsData
        .map(d => ({
          ...d,
          entries: d.entries.filter(e => e.category !== 'poster'),
          total: d.entries.filter(e => e.category !== 'poster').length,
        }))
        .filter(d => d.entries.length > 0)
    },

    // Every day that has content in the active pool, with its per-day total.
    allDaysGlobal() {
      const grouped = {}
      for (const d of this.universeRoomsData) {
        ;(grouped[d.day] = grouped[d.day] || []).push(d)
      }
      return DAY_ORDER.filter(day => grouped[day]).map(day => ({
        day,
        total: grouped[day].reduce((s, r) => s + r.total, 0),
        isPast: this.isDayPast(day),
      }))
    },

    dayCounts() {
      return this.allDaysGlobal.reduce((m, d) => ((m[d.day] = d.total), m), {})
    },

    pastDaysCount() {
      return this.allDaysGlobal.filter(d => d.isPast).length
    },

    dayFilterChips() {
      // With no search, past days stay collapsed until asked for. During a
      // search the user explicitly wants to reach everything, so don't hide.
      const days = this.allDaysGlobal.filter(d => this.query || this.showPastDays || !d.isPast)
      return [ALL_DAYS, ...days.map(d => d.day)]
    },

    // Rooms that actually have content in the active pool (day-agnostic), so
    // the select never offers a room that would render an empty page.
    roomFilterChips() {
      const rooms = new Set()
      for (const d of this.universeRoomsData) for (const e of d.entries) if (e.room) rooms.add(e.room)
      return [ALL_ROOMS, ...[...rooms].sort((a, b) => a.localeCompare(b))]
    },

    // The final, visible day → room → entry tree. Entries are ordered with
    // slides first (the ready-to-watch talks float to the top), then by code.
    roomDays() {
      const q = this.query.trim().toLowerCase()
      const searching = q.length > 0

      const grouped = {}
      for (const d of this.universeRoomsData) {
        // A search deliberately spans every day, room and category: someone
        // looking for their own name should not have to guess which day, room
        // or category they're filed under.
        if (!searching && this.activeRoom !== ALL_ROOMS && d.room !== this.activeRoom) continue
        if (!searching && this.activeDay !== ALL_DAYS && d.day !== this.activeDay) continue

        const entries = (searching ? d.entries.filter(e => this.matches(e, q)) : d.entries)
          .slice()
          .sort((a, b) => {
            if (!!a.has_presentation !== !!b.has_presentation) return b.has_presentation ? 1 : -1
            return (a.code || '').localeCompare(b.code || '', undefined, { numeric: true })
          })
        if (!entries.length) continue

        grouped[d.day] = grouped[d.day] || []
        grouped[d.day].push({
          ...d,
          entries,
          total: entries.length,
          with_slide: entries.filter(e => e.has_presentation).length,
        })
      }

      return DAY_ORDER.filter(day => grouped[day])
        .filter(day => searching || this.showPastDays || !this.isDayPast(day))
        .map(day => ({
          day,
          rooms: grouped[day],
          total: grouped[day].reduce((s, r) => s + r.total, 0),
          isPast: this.isDayPast(day),
        }))
    },

    totalShown() {
      return this.roomDays.reduce((s, d) => s + d.total, 0)
    },

    // Deliberately excludes entryCategory: the category tabs are primary
    // navigation, not a filter to be reset out from under someone browsing
    // posters on purpose.
    hasNonDefaultFilters() {
      return this.activeDay !== ALL_DAYS || this.activeRoom !== ALL_ROOMS || this.query.trim().length > 0
    },

    dateRange() {
      if (!this.eventStartDate) return ''
      const year = new Date(this.eventStartDate + 'T00:00:00').getFullYear()
      if (!this.eventEndDate || this.eventEndDate === this.eventStartDate) {
        return `${this.formatDate(this.eventStartDate)} ${year}`
      }
      return `${this.formatDate(this.eventStartDate)} – ${this.formatDate(this.eventEndDate)} ${year}`
    },

    // Past days suppressed purely by the collapse policy. Must not fire when
    // past days are already shown, or when the user has deliberately picked a
    // single day — otherwise the line contradicts the "Hide past days" toggle.
    hiddenPastCount() {
      if (this.query || this.showPastDays || this.activeDay !== ALL_DAYS) return 0
      return this.allDaysGlobal.filter(d => d.isPast).length
    },
  },

  watch: {
    // Switching category changes which rooms/days even have content, so drop
    // the now-meaningless day/room selection instead of showing an empty page.
    entryCategory() {
      this.activeRoom = ALL_ROOMS
      this.activeDay = ALL_DAYS
    },
    roomDays: 'syncUrl',
    showPastDays: 'syncUrl',
    activeRoom: 'syncUrl',
  },

  mounted() {
    // One page-view record per open (ref/src come from the certificate-email link).
    this.trackOpen()
    this.readUrl()
    window.addEventListener('scroll', this.onScroll, { passive: true })
    window.addEventListener('keydown', this.onKeydown)
    this.load()
  },

  beforeUnmount() {
    window.removeEventListener('scroll', this.onScroll)
    window.removeEventListener('keydown', this.onKeydown)
  },

  methods: {
    onScroll() {
      this.showTopButton = window.scrollY > 700
    },

    onKeydown(e) {
      if (e.key === '/' && !/^(INPUT|SELECT|TEXTAREA)$/.test(e.target?.tagName || '')) {
        e.preventDefault()
        this.$refs.searchInput?.focus()
      } else if (e.key === 'Escape' && this.query) {
        this.query = ''
      }
    },

    scrollToTop() {
      window.scrollTo({ top: 0, behavior: 'smooth' })
    },

    resetFilters() {
      this.query = ''
      this.activeDay = ALL_DAYS
      this.activeRoom = ALL_ROOMS
    },

    // Keep the filters in the URL so a view can be bookmarked or shared.
    // Routed through the router (not history.replaceState) so the router's
    // own view of the URL stays authoritative.
    syncUrl() {
      const q = { event_id: this.eventId }
      if (this.entryCategory !== 'oral') q.cat = this.entryCategory
      if (this.activeDay !== ALL_DAYS) q.day = this.activeDay
      if (this.activeRoom !== ALL_ROOMS) q.room = this.activeRoom
      if (this.query.trim()) q.q = this.query.trim()
      const same = JSON.stringify({ ...this.$route.query, ...q }) === JSON.stringify(this.$route.query)
      if (same) return
      const nav = this.$router.replace({ query: q })
      if (nav && typeof nav.catch === 'function') nav.catch(() => {})
    },

    readUrl() {
      const q = this.$route.query
      if (q.cat && this.categoryOptions.some(c => c.key === q.cat)) this.entryCategory = q.cat
      if (q.day) this.activeDay = q.day
      if (q.room) this.activeRoom = q.room
      if (q.q) this.query = String(q.q)
    },

    matches(entry, q) {
      return [
        entry.title, entry.activity, entry.presenter_name, entry.original_presenter,
        entry.code, entry.session, entry.room, entry.theme, entry.role,
      ].some(v => v && String(v).toLowerCase().includes(q))
    },

    // Splits text into matched/unmatched runs so search hits can be <mark>ed
    // with plain templates — no v-html, so titles stay un-injectable.
    splitHighlight(text) {
      const s = String(text || '')
      const q = this.query.trim()
      if (!q) return [{ t: s, hit: false }]
      const out = []
      const needle = q.toLowerCase()
      let i = 0
      while (i < s.length) {
        const at = s.toLowerCase().indexOf(needle, i)
        if (at === -1) { out.push({ t: s.slice(i), hit: false }); break }
        if (at > i) out.push({ t: s.slice(i, at), hit: false })
        out.push({ t: s.slice(at, at + q.length), hit: true })
        i = at + q.length
      }
      return out
    },

    formatDate(d) {
      return new Date(d + 'T00:00:00').toLocaleDateString('en-GB', { day: 'numeric', month: 'short' })
    },

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

    // Records one open for the admin's page-view stats (POST /page-views/).
    // visitor_id is a random per-browser id so repeat opens count as one
    // visitor; ref/src come from the certificate-email link. Fire-and-forget:
    // tracking must never affect the page.
    trackOpen() {
      let visitorId = null
      try {
        visitorId = localStorage.getItem('ecsa_visitor_id')
        if (!visitorId) {
          visitorId = (crypto.randomUUID && crypto.randomUUID()) ||
            `${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 12)}`
          localStorage.setItem('ecsa_visitor_id', visitorId)
        }
      } catch (e) { /* storage blocked — still count the open, just not uniquely */ }
      const q = this.$route.query
      axios.post(`${this.apiUrl}/page-views/`, {
        page: 'programme-rooms-public',
        event_id: Number(this.eventId) || null,
        visitor_id: visitorId,
        ref: q.ref ? String(q.ref) : null,
        source: q.src === 'email' ? 'email' : 'direct',
      }).catch(() => {})
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
        // If the conference has already started, Day 1 is a "past day" and
        // would be hidden by default — without this the default All Days view
        // would silently render an empty page.
        if (this.allDaysGlobal.some(d => d.isPast)) this.showPastDays = true
      } catch (e) {
        this.loadError = e.response?.data?.detail || 'Failed to load the programme.'
      } finally {
        this.loading = false
      }
    },

    isPreviewable(ext) {
      const e = (ext || '').replace(/^\./, '').toLowerCase()
      return ['pdf', 'ppt', 'pptx', 'jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp'].includes(e)
    },

    // Inline types render straight in the iframe; Office formats (ppt/pptx)
    // go through the Microsoft Office Online embed viewer, which fetches the
    // public preview URL itself — same approach as the admin Rooms page.
    previewSrc(entry) {
      const ext = (entry.presentation_ext || '').replace(/^\./, '').toLowerCase()
      const fileUrl = `${this.apiUrl}/programme/${entry.id}/preview-presentation`
      return ['pdf', 'jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp'].includes(ext)
        ? fileUrl
        : `https://view.officeapps.live.com/op/embed.aspx?src=${encodeURIComponent(fileUrl)}`
    },

    openPreview(entry) {
      if (!this.isPreviewable(entry.presentation_ext)) {
        this.downloadFlash = 'Preview not supported for this file type — use Download instead.'
        setTimeout(() => { this.downloadFlash = '' }, 4000)
        return
      }
      this.preview = { open: true, name: entry.title || entry.presenter_name, src: this.previewSrc(entry) }
    },

    async downloadSingle(entry) {
      this.downloadProgress = { active: true, label: entry.title || entry.presenter_name || 'presentation', percent: 0, loadedMB: '0.0', totalMB: null }
      try {
        const res = await axios.get(`${this.apiUrl}/programme/${entry.id}/download-presentation`, {
          responseType: 'blob',
          onDownloadProgress: (evt) => {
            this.downloadProgress.loadedMB = (evt.loaded / 1048576).toFixed(1)
            if (evt.total) {
              this.downloadProgress.totalMB = (evt.total / 1048576).toFixed(1)
              this.downloadProgress.percent = Math.round((evt.loaded / evt.total) * 100)
            }
          },
        })
        const ext = (entry.presentation_ext || '').replace(/^\./, '')
        const clean = (entry.code || entry.presenter_name || 'presentation').replace(/[^A-Za-z0-9 _-]+/g, '').trim().slice(0, 60)
        saveAs(res.data, `${clean || 'presentation'}.${ext}`)
      } catch (e) {
        this.loadError = 'Download failed.'
      } finally {
        this.downloadProgress.active = false
      }
    },

    async downloadRoomZip(room) {
      this.zipBusy = true
      this.zipProgress = { active: true, room: room.room || 'All Rooms', percent: 0, loadedMB: '0.0', totalMB: null }
      try {
        const res = await axios.get(`${this.apiUrl}/programme/download-room-zip`, {
          params: { event_id: this.eventId, room: room.room, day: room.day },
          responseType: 'blob',
          onDownloadProgress: (evt) => {
            this.zipProgress.loadedMB = (evt.loaded / 1048576).toFixed(1)
            if (evt.total) {
              this.zipProgress.totalMB = (evt.total / 1048576).toFixed(1)
              this.zipProgress.percent = Math.round((evt.loaded / evt.total) * 100)
            }
          },
        })
        saveAs(res.data, `${(room.room || 'room').replace(/[^A-Za-z0-9_]+/g, '_')}_slides.zip`)
      } catch (e) {
        this.loadError = 'No slides to download for this room yet.'
      } finally {
        this.zipBusy = false
        this.zipProgress.active = false
      }
    },
  },
}
</script>

<style scoped>
.badge-sub {
  @apply inline-flex items-center px-1.5 py-0.5 rounded text-[10px] font-bold uppercase tracking-wide bg-purple-100 text-purple-700;
}
.act {
  @apply inline-flex items-center gap-1 px-2.5 py-1.5 rounded-lg text-xs font-semibold border transition whitespace-nowrap;
}
.act-preview {
  @apply act border-transparent text-white;
  background-color: rgb(0,150,180);
}
.act-preview:hover { @apply opacity-90; }
.act-download {
  @apply act border-gray-200 text-gray-600 bg-white;
}
.act-download:hover { @apply border-gray-400 text-gray-900; }
.act-video {
  @apply act border-transparent text-white;
  background-color: rgb(100,60,180);
}
.act-video:hover { @apply opacity-90; }
kbd {
  @apply font-sans font-semibold text-gray-500;
}
mark {
  @apply font-semibold;
}
</style>
