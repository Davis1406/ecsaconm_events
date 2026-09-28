<template>
  <div class="flex flex-col space-y-4 flex-1">
    <HeaderView :headerTitle="'Presentations by Room'" />

    <div v-if="flashMsg" class="px-3 py-2 rounded-md text-sm"
      :class="flashErr ? 'bg-red-50 text-red-600' : 'bg-green-50 text-green-600'">
      {{ flashMsg }}
    </div>

    <!-- Rooms view -->
      <!-- category toggle: abstracts (oral) vs posters -->
      <div class="flex items-center gap-2">
        <button v-for="c in categoryOptions" :key="c.key"
          @click="entryCategory = c.key"
          class="chip" :class="entryCategory === c.key ? 'chip--active' : 'chip--idle'">
          {{ c.label }}
        </button>
      </div>

      <!-- day filter chips -->
      <div class="flex flex-wrap items-center gap-2">
        <button v-for="d in dayFilterChips" :key="d"
          @click="activeDay = d"
          class="chip" :class="activeDay === d ? 'chip--active' : 'chip--idle'">
          {{ d }}
        </button>
        <button v-if="pastDaysCount > 0" @click="showPastDays = !showPastDays"
          class="text-xs font-semibold hover:underline" style="color: rgb(0,150,180);">
          {{ showPastDays ? 'Hide past days' : `Show ${pastDaysCount} past day${pastDaysCount !== 1 ? 's' : ''}` }}
        </button>
      </div>

      <!-- room summary chips -->
      <div class="flex flex-wrap items-center gap-2">
        <button v-for="r in roomFilterChips" :key="r"
          @click="activeRoom = r"
          class="chip" :class="activeRoom === r ? 'chip--active' : 'chip--idle'">
          {{ r }}
        </button>
        <div class="flex-1"></div>
        <button @click="copyPublicProgrammeLink"
          class="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-semibold border"
          style="border-color: rgb(0,150,180); color: rgb(0,150,180);"
          title="Copy a no-login link showing every room/day, view-only">
          <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M13.828 10.172a4 4 0 010 5.656l-3 3a4 4 0 01-5.656-5.656l1.5-1.5M10.172 13.828a4 4 0 010-5.656l3-3a4 4 0 015.656 5.656l-1.5 1.5"/>
          </svg>
          Share Full Programme
        </button>
        <button v-if="isAdmin" @click="runBackfillRooms" :disabled="backfillBusy"
          class="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-semibold border disabled:opacity-50"
          style="border-color: rgb(180,120,0); color: rgb(150,100,0);"
          title="Fill in Unassigned entries' rooms from the official programme PDF, matched by abstract code — never overwrites an existing room">
          <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.75">
            <path stroke-linecap="round" stroke-linejoin="round" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"/><path stroke-linecap="round" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"/>
          </svg>
          {{ backfillBusy ? 'Filling rooms…' : 'Fill Unassigned Rooms from Programme' }}
        </button>
        <button v-if="isAdmin" @click="openAdd" :disabled="addBusy"
          class="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-semibold border"
          style="border-color: rgb(34,197,94); color: rgb(16,150,60);">
          <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M12 4v16m8-8H4" />
          </svg>
          Add Presenter
        </button>
        <button v-if="isAdmin" @click="openAssignPresenters" :disabled="assignBusy"
          class="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-semibold border"
          style="border-color: rgb(254,80,103); color: rgb(254,80,103);">
          <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.75">
            <path stroke-linecap="round" stroke-linejoin="round" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
          </svg>
          Assign to Room
        </button>
        <button v-if="isAdmin && entryCategory !== 'plenary'" @click="openMatch" :disabled="matchLoading"
          class="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-semibold border"
          style="border-color: rgb(0,150,180); color: rgb(0,150,180);"
          title="Matches an oral/poster schedule slot to its submitted abstract — doesn't apply to invited plenary speakers">
          <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.75">
            <path stroke-linecap="round" stroke-linejoin="round" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          {{ matchLoading ? 'Matching…' : `Match ${entryCategory === 'poster' ? 'Posters' : 'Abstracts'}` }}
        </button>
        <button v-if="isAdmin" @click="openBulkUpload"
          class="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-semibold border"
          style="border-color: rgb(120,80,200); color: rgb(100,60,180);"
          title="Select a folder of local presentation/video files and match+upload them to the right entry in one go">
          <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.75">
            <path stroke-linecap="round" stroke-linejoin="round" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M12 12v9m0-9l-3 3m3-3l3 3"/>
          </svg>
          Bulk Match & Upload
        </button>
        <span class="text-xs text-gray-500">{{ slideCountSummary }}</span>
      </div>

      <div v-if="loading" class="py-10"><SpinnerComponent /></div>

      <div v-else class="space-y-5">
        <!-- Per day -->
        <div v-for="day in roomDays" :key="day.day" class="space-y-4">
          <div class="flex items-center gap-2">
            <div class="px-3 py-1 rounded-full text-xs font-bold text-white" :style="{ backgroundColor: dayColor(day.day) }">
              {{ day.day }}
            </div>
            <div class="text-xs text-gray-500">{{ day.rooms.length }} room{{ day.rooms.length !== 1 ? 's' : '' }} · {{ day.total }} presentations</div>
          </div>

          <div class="grid grid-cols-1 lg:grid-cols-2 gap-4">
            <!-- per room -->
            <div v-for="room in day.rooms" :key="room.day + room.room"
              class="rounded-xl border border-surface-container-high bg-surface-container-lowest overflow-hidden">
              <div class="px-4 py-3 flex items-center justify-between border-b border-gray-100"
                style="background-color: rgb(0,150,180);">
                <div class="font-bold text-white flex items-center gap-2">
                  <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.75">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"/><path stroke-linecap="round" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"/>
                  </svg>
                  {{ room.room }}
                </div>
                <div class="flex items-center gap-2">
                  <span class="text-[11px] text-white/90 font-medium">{{ room.total }}</span>
                  <button @click="copyRoomLink(room)"
                    class="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-[11px] font-semibold bg-white/15 text-white hover:bg-white/25" title="Copy a shareable link for this room's leader">
                    <svg class="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                      <path stroke-linecap="round" stroke-linejoin="round" d="M13.828 10.172a4 4 0 010 5.656l-3 3a4 4 0 01-5.656-5.656l1.5-1.5M10.172 13.828a4 4 0 010-5.656l3-3a4 4 0 015.656 5.656l-1.5 1.5"/>
                    </svg>
                    Share
                  </button>
                  <button @click="exportRoomPDF(room)" :disabled="pdfBusy === room.day + room.room"
                    class="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-[11px] font-semibold bg-white/15 text-white hover:bg-white/25 disabled:opacity-50" title="Export this room's presenter list as a PDF with ECSA branding">
                    <svg class="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                      <path stroke-linecap="round" stroke-linejoin="round" d="M17 17h2a2 2 0 002-2v-4a2 2 0 00-2-2H5a2 2 0 00-2 2v4a2 2 0 002 2h2m2 4h6a2 2 0 002-2v-4a2 2 0 00-2-2H9a2 2 0 00-2 2v4a2 2 0 002 2zm8-12V3a1 1 0 00-1-1H8a1 1 0 00-1 1v3h10z" />
                    </svg>
                    {{ pdfBusy === room.day + room.room ? '…' : 'PDF' }}
                  </button>
                  <button v-if="room.with_slide" @click="downloadRoomZip(room)"
                    :disabled="zipBusy"
                    class="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-[11px] font-semibold bg-white text-cp-secondary hover:opacity-90">
                    <svg class="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                      <path stroke-linecap="round" stroke-linejoin="round" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"/>
                    </svg>
                    All slides
                  </button>
                  <button v-if="isAdmin" @click="deleteRoom(room)" :disabled="roomDeleting === room.room"
                    title="Delete every entry in this room"
                    class="inline-flex items-center gap-1 px-2 py-1 rounded-full text-[11px] font-semibold bg-white/15 text-white hover:bg-red-500/80 disabled:opacity-50">
                    <svg class="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                      <path stroke-linecap="round" stroke-linejoin="round" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/>
                    </svg>
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
                      <span v-if="e.status === 'not_registered'" class="badge badge-warn" title="Name not matched to a registered person">⚠</span>
                    </div>
                    <div class="text-xs text-gray-500 mt-0.5 flex flex-wrap items-center gap-x-2 gap-y-0.5">
                      <span v-if="e.code" class="font-mono">{{ e.code }}</span>
                      <span v-if="e.session">Session {{ e.session }}</span>
                      <span v-if="e.category === 'poster'" class="uppercase tracking-wide text-amber-600">Poster</span>
                      <span v-if="e.category === 'plenary' && e.role" class="italic">{{ e.role }}</span>
                    </div>
                    <div class="text-sm text-on-surface mt-1">{{ e.title || e.activity || '' }}</div>
                  </div>
                  <div class="flex items-center gap-1">
                    <button v-if="e.has_presentation"
                      @click="openPreview(e)"
                      class="action-btn hover:border-cp-secondary" :title="e.presentation_source === 'abstract' ? 'Preview slides (from submitted abstract)' : 'Preview slides'">
                      <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.75">
                        <path stroke-linecap="round" stroke-linejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/><path stroke-linecap="round" stroke-linejoin="round" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"/>
                      </svg>
                    </button>
                    <button v-if="e.has_presentation"
                      @click="downloadSingle(e)"
                      class="action-btn hover:border-cp-secondary" :title="e.presentation_source === 'abstract' ? 'Download slides (from submitted abstract)' : 'Download slides'">
                      <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.75">
                        <path stroke-linecap="round" stroke-linejoin="round" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"/>
                      </svg>
                    </button>
                    <a v-if="e.video_url" :href="e.video_url" target="_blank" rel="noopener"
                      class="action-btn hover:border-cp-secondary" title="Watch video" style="color: rgb(120,80,200); border-color: rgb(120,80,200);">
                      <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.75">
                        <path stroke-linecap="round" stroke-linejoin="round" d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z"/>
                      </svg>
                    </a>
                    <span v-if="!e.has_presentation && !e.video_url" class="text-[10px] text-gray-400 italic">no slides yet</span>
                    <span v-else-if="e.presentation_source === 'abstract'" class="text-[9px] text-teal-600 font-semibold uppercase tracking-wide">from abstract</span>
                    <button @click="openManage(e)" title="Replace presenter / add slides"
                      class="action-btn hover:border-cp-secondary">
                      <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.75">
                        <path stroke-linecap="round" stroke-linejoin="round" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                      </svg>
                    </button>
                    <button v-if="isAdmin" @click="deleteEntry(e)" :disabled="entryDeleting === e.id"
                      title="Delete this entry"
                      class="action-btn hover:border-red-400 hover:text-red-500 disabled:opacity-50">
                      <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.75">
                        <path stroke-linecap="round" stroke-linejoin="round" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/>
                      </svg>
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

    <!-- Match to Abstracts modal -->
    <div v-if="matchOpen" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/40" @click.self="matchOpen = false">
      <div class="bg-white rounded-xl shadow-xl w-full max-w-2xl max-h-[88vh] overflow-y-auto">
        <div class="px-5 py-4 border-b border-gray-100 flex items-center justify-between sticky top-0 bg-white">
          <div>
            <div class="font-bold">Match Presenters to Abstracts — {{ entryCategory === 'poster' ? 'Posters' : 'Abstracts' }}</div>
            <p class="text-xs text-gray-500 mt-0.5">
              Matches each {{ entryCategory === 'poster' ? 'poster' : 'oral' }} schedule slot to its submitted abstract by
              presenter name (titles are ignored — the schedule book's wording often differs
              from the submitted title). Corrects the presenter name to what's on file.
            </p>
          </div>
          <button @click="matchOpen = false" class="text-gray-400 hover:text-gray-600 flex-shrink-0 ml-3">
            <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" d="M6 18L18 6M6 6l12 12"/></svg>
          </button>
        </div>
        <div class="p-5 space-y-4">
          <div v-if="matchLoading" class="py-10"><SpinnerComponent /></div>
          <template v-else-if="matchReport">
            <div class="grid grid-cols-3 gap-2 text-center">
              <div class="rounded-lg bg-teal-50 p-3">
                <div class="text-xl font-bold text-teal-700">{{ matchReport.matches.length }}</div>
                <div class="text-[11px] text-teal-700/80">matched</div>
              </div>
              <div class="rounded-lg bg-amber-50 p-3">
                <div class="text-xl font-bold text-amber-700">{{ matchReport.unmatched_entries.length }}</div>
                <div class="text-[11px] text-amber-700/80">slots w/o abstract</div>
              </div>
              <div class="rounded-lg bg-orange-50 p-3">
                <div class="text-xl font-bold text-orange-700">{{ matchReport.unmatched_abstracts.length }}</div>
                <div class="text-[11px] text-orange-700/80">abstracts w/o slot</div>
              </div>
            </div>

            <div v-if="matchApplyResult" class="px-3 py-2 rounded-md bg-green-50 text-green-700 text-sm">
              Applied — {{ matchApplyResult.renamed }} name{{ matchApplyResult.renamed === 1 ? '' : 's' }} corrected,
              {{ matchApplyResult.linked }} newly linked to an abstract.
            </div>

            <div v-if="matchReport.matches.length" class="space-y-2">
              <div class="flex items-center justify-between">
                <div class="font-semibold text-sm">Proposed matches — confirm each one</div>
                <div class="text-xs space-x-2">
                  <button @click="setAllMatchSelected(true)" class="text-cp-secondary font-medium hover:underline">Select all</button>
                  <button @click="setAllMatchSelected(false)" class="text-gray-400 font-medium hover:underline">Select none</button>
                </div>
              </div>
              <p class="text-xs text-gray-500">
                Untick anything that doesn't look right — it's left alone and
                still shows up next time. Where the presenter already uploaded
                slides, use Preview to check it's really them before confirming.
              </p>
              <div class="rounded-lg border border-gray-200 divide-y divide-gray-100 max-h-72 overflow-y-auto">
                <label v-for="m in matchReport.matches" :key="m.entry_id"
                  class="px-3 py-2 text-sm flex items-start gap-2.5 cursor-pointer hover:bg-gray-50">
                  <input type="checkbox" v-model="matchSelected[m.entry_id]" class="mt-1 accent-cp-secondary flex-shrink-0" />
                  <div class="flex-1 min-w-0">
                    <div class="flex items-center gap-2 flex-wrap">
                      <span class="font-mono text-xs text-gray-400">{{ m.code || '—' }}</span>
                      <template v-if="m.name_changed">
                        <span class="text-gray-400 line-through">{{ m.current_presenter_name }}</span>
                        <span>→</span>
                        <span class="font-semibold">{{ m.corrected_name }}</span>
                      </template>
                      <span v-else class="font-semibold">{{ m.corrected_name }}</span>
                      <span class="text-[10px] text-gray-400 ml-auto">score {{ m.score }}</span>
                    </div>
                    <div class="text-xs text-gray-500 truncate mt-0.5">{{ m.abstract_title }}</div>
                    <button v-if="m.abstract_has_presentation" @click.prevent="previewAbstract(m)"
                      class="inline-flex items-center gap-1 mt-1 px-2 py-0.5 rounded-full text-[11px] font-semibold border"
                      style="border-color: rgb(0,150,180); color: rgb(0,150,180);">
                      Preview their slides
                    </button>
                    <span v-else class="inline-block mt-1 text-[11px] text-gray-400 italic">no slides uploaded yet</span>
                  </div>
                </label>
              </div>
            </div>

            <div v-if="matchReport.unmatched_entries.length" class="space-y-2">
              <div class="font-semibold text-sm text-amber-700">Schedule slots with no matching abstract</div>
              <p class="text-xs text-gray-500">
                Pick the right abstract from the list below and link it manually
                — the presenter name will be corrected the same way an automatic
                match would.
              </p>
              <div class="rounded-lg border border-amber-100 bg-amber-50/50 divide-y divide-amber-100 max-h-72 overflow-y-auto">
                <div v-for="u in matchReport.unmatched_entries" :key="u.entry_id" class="px-3 py-2 text-sm space-y-1.5">
                  <div>
                    <span class="font-mono text-xs text-gray-400 mr-2">{{ u.code || '—' }}</span>
                    <span class="font-semibold">{{ u.presenter_name || '—' }}</span>
                    <div class="text-xs text-gray-500 truncate">{{ u.title }}</div>
                  </div>
                  <div v-if="matchReport.unmatched_abstracts.length" class="flex items-center gap-2">
                    <select v-model="linkChoice[u.entry_id]" class="field-input !py-1 !text-xs flex-1">
                      <option value="">Match to abstract…</option>
                      <option v-for="a in matchReport.unmatched_abstracts" :key="a.abstract_id" :value="a.abstract_id">
                        {{ a.presenter }} — {{ (a.title || '').slice(0, 50) }}
                      </option>
                    </select>
                    <button @click="linkAbstract(u.entry_id)" :disabled="!linkChoice[u.entry_id] || linkBusy"
                      class="px-2.5 py-1 text-xs font-semibold rounded-full text-white flex-shrink-0"
                      style="background-color: rgb(0,150,180);">
                      Link
                    </button>
                  </div>
                </div>
              </div>
            </div>

            <div v-if="matchReport.unmatched_abstracts.length" class="space-y-2">
              <div class="font-semibold text-sm text-orange-700">Accepted abstracts with no schedule slot</div>
              <div class="rounded-lg border border-orange-100 bg-orange-50/50 divide-y divide-orange-100 max-h-40 overflow-y-auto">
                <div v-for="u in matchReport.unmatched_abstracts" :key="u.abstract_id" class="px-3 py-2 text-sm">
                  <span class="font-semibold">{{ u.presenter }}</span>
                  <span v-if="u.has_presentation" class="text-[10px] text-teal-600 font-semibold uppercase tracking-wide ml-1">has slides</span>
                  <div class="text-xs text-gray-500 truncate">{{ u.title }}</div>
                </div>
              </div>
            </div>
          </template>
          <div v-if="matchErr" class="px-3 py-2 rounded-md bg-red-50 text-red-600 text-sm">{{ matchErr }}</div>
        </div>
        <div class="px-5 py-4 border-t border-gray-100 flex justify-end gap-2 sticky bottom-0 bg-white">
          <button @click="matchOpen = false" class="px-4 py-2 text-sm font-medium text-gray-600 hover:bg-gray-50 rounded-lg">Close</button>
          <button v-if="matchReport && matchReport.matches.length" @click="applyMatch" :disabled="matchApplying || selectedMatchCount === 0"
            class="px-4 py-2 text-sm font-semibold text-white rounded-lg disabled:opacity-50" style="background-color: rgb(254,80,103);">
            {{ matchApplying ? 'Applying…' : `Confirm ${selectedMatchCount} match${selectedMatchCount === 1 ? '' : 'es'}` }}
          </button>
        </div>
      </div>
    </div>

    <!-- Assign to Room modal -->
    <div v-if="assignOpen" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/40" @click.self="assignOpen = false">
      <div class="bg-white rounded-xl shadow-xl w-full max-w-3xl max-h-[90vh] overflow-y-auto">
        <div class="px-5 py-4 border-b border-gray-100 flex items-center justify-between sticky top-0 bg-white z-10">
          <div>
            <div class="font-bold">Assign Uploaded Presentations to a Room</div>
            <p class="text-xs text-gray-500 mt-0.5">
              Pick the day, pick the room from that day's programme, then tick the presenters whose slides go into it.
            </p>
          </div>
          <button @click="assignOpen = false" class="text-gray-400 hover:text-gray-600 flex-shrink-0 ml-3">
            <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" d="M6 18L18 6M6 6l12 12"/></svg>
          </button>
        </div>
        <div class="p-5 space-y-4">
          <!-- Step 1 — day -->
          <div class="rounded-lg border border-gray-200 p-4 space-y-2">
            <div class="flex items-center gap-2">
              <span class="w-5 h-5 rounded-full text-white text-[10px] font-bold flex items-center justify-center" style="background-color: rgb(254,80,103);">1</span>
              <div class="font-semibold text-sm">Pick the day</div>
            </div>
            <div class="flex flex-wrap items-center gap-2 pl-7">
              <button v-for="d in assignDays" :key="d"
                @click="selectAssignDay(d)"
                class="chip" :class="assignForm.day === d ? 'chip--active' : 'chip--idle'">
                {{ d }}
              </button>
            </div>
          </div>

          <!-- Step 2 — room -->
          <div class="rounded-lg border border-gray-200 p-4 space-y-2">
            <div class="flex items-center gap-2">
              <span class="w-5 h-5 rounded-full text-white text-[10px] font-bold flex items-center justify-center" style="background-color: rgb(254,80,103);">2</span>
              <div class="font-semibold text-sm">Pick the room — {{ assignForm.day }}</div>
            </div>
            <div class="flex flex-wrap items-center gap-2 pl-7">
              <button v-for="d in assignRoomsForDay" :key="d.room"
                @click="selectAssignRoom(d.room)"
                class="chip" :class="assignForm.room === d.room ? 'chip--active' : 'chip--idle'"
                :title="`${d.total} slot${d.total === 1 ? '' : 's'} · ${d.with_slide} with slides`">
                {{ d.room }}
                <span class="ml-1 text-[10px] font-medium opacity-70">{{ d.total }}</span>
              </button>
              <input v-model.trim="assignForm.room" type="text" class="field-input !py-1.5 !text-xs !w-44" placeholder="or type a new room…" />
            </div>
            <div v-if="!assignRoomsForDay.length" class="pl-7 text-xs text-gray-400">
              No rooms scheduled for {{ assignForm.day }} yet — type a room name above to create one.
            </div>
          </div>

          <!-- Step 3 — presenters -->
          <div class="rounded-lg border border-gray-200 p-4 space-y-2">
            <div class="flex items-center gap-2">
              <span class="w-5 h-5 rounded-full text-white text-[10px] font-bold flex items-center justify-center" style="background-color: rgb(254,80,103);">3</span>
              <div class="font-semibold text-sm">Tick the presenters to assign{{ assignForm.room ? ` to ${assignForm.room} · ${assignForm.day}` : '' }}</div>
            </div>

            <div v-if="assignLoading" class="py-10"><SpinnerComponent /></div>
            <template v-else>
              <!-- Category + search -->
              <div class="flex flex-wrap items-center gap-2 pl-7">
                <button v-for="c in assignCategoryOptions" :key="c.key"
                  @click="assignCategory = c.key"
                  class="chip" :class="assignCategory === c.key ? 'chip--active' : 'chip--idle'">
                  {{ c.label }} ({{ c.count }})
                </button>
                <div class="relative flex-1 min-w-[160px]">
                  <svg class="w-3.5 h-3.5 text-gray-400 absolute left-2.5 top-1/2 -translate-y-1/2" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/>
                  </svg>
                  <input v-model.trim="assignSearch" type="text" class="field-input !py-1.5 !text-xs !pl-8" placeholder="Search presenter or abstract…" />
                </div>
                <div class="flex-1"></div>
                <div class="text-xs text-gray-500 space-x-2">
                  <button @click="setAssignAll(true)" class="font-medium hover:underline" style="color: rgb(0,150,180);">Select all shown</button>
                  <button @click="setAssignAll(false)" class="text-gray-400 font-medium hover:underline">Select none</button>
                </div>
              </div>

              <!-- Presenter list -->
              <div class="rounded-lg border border-gray-200 divide-y divide-gray-100 max-h-72 overflow-y-auto">
                <div v-if="assignFilteredRows.length === 0" class="px-4 py-6 text-center text-sm text-gray-400 italic">
                  No presenters match your search or filter.
                </div>
                <label v-for="r in assignFilteredRows" :key="r.abstract_id"
                  class="px-4 py-3 text-sm flex items-start gap-3 cursor-pointer hover:bg-gray-50">
                  <input type="checkbox" v-model="assignSelected[r.abstract_id]" class="mt-1 accent-cp-secondary flex-shrink-0" />
                  <div class="flex-1 min-w-0">
                    <div class="flex flex-wrap items-center gap-x-2 gap-y-0.5">
                      <span class="font-semibold">{{ r.presenter }}</span>
                      <span v-if="r.presentation_ext" class="text-[10px] font-semibold px-1.5 py-0.5 rounded bg-gray-100 text-gray-600 uppercase">{{ r.presentation_ext }}</span>
                      <span class="text-[10px] font-semibold px-1.5 py-0.5 rounded uppercase"
                        :class="r.presentation_type === 'poster' ? 'bg-amber-100 text-amber-700' : 'bg-blue-100 text-blue-700'">
                        {{ r.presentation_type }}
                      </span>
                    </div>
                    <div class="text-xs text-gray-500 truncate mt-0.5">{{ r.title }}</div>
                  </div>
                  <button v-if="r.has_presentation" @click.prevent.stop="previewAssignAbstract(r)"
                    class="text-[11px] font-semibold px-2 py-0.5 rounded-full border flex-shrink-0"
                    style="border-color: rgb(0,150,180); color: rgb(0,150,180);">
                    Preview
                  </button>
                </label>
              </div>
            </template>
          </div>

          <div v-if="assignDone" class="px-3 py-2 rounded-md bg-green-50 text-green-700 text-sm">{{ assignDone }}</div>
          <div v-if="assignErr" class="px-3 py-2 rounded-md bg-red-50 text-red-600 text-sm">{{ assignErr }}</div>
        </div>
        <div class="px-5 py-4 border-t border-gray-100 flex justify-end gap-2 sticky bottom-0 bg-white">
          <button @click="assignOpen = false" class="px-4 py-2 text-sm font-medium text-gray-600 hover:bg-gray-50 rounded-lg">Close</button>
          <button v-if="assignForm.room" @click="submitAssign" :disabled="assignBusy || assignSelectedCount === 0"
            class="px-4 py-2 text-sm font-semibold text-white rounded-lg disabled:opacity-50"
            style="background-color: rgb(254,80,103);">
            {{ assignBusy ? 'Assigning…' : `Assign ${assignSelectedCount} to ${assignForm.day} · ${assignForm.room}` }}
          </button>
        </div>
      </div>
    </div>

    <!-- Add presenter (manual entry) modal -->
    <div v-if="addOpen" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/40" @click.self="closeAdd">
      <div class="bg-white rounded-xl shadow-xl w-full max-w-lg max-h-[90vh] overflow-y-auto">
        <div class="px-5 py-4 border-b border-gray-100 flex items-center justify-between">
          <div>
            <div class="font-bold">Add Presenter</div>
            <p class="text-xs text-gray-500 mt-0.5">
              Manually add a presenter who wasn't in the programme, and attach their slides.
            </p>
          </div>
          <button @click="closeAdd" class="text-gray-400 hover:text-gray-600">
            <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" d="M6 18L18 6M6 6l12 12"/></svg>
          </button>
        </div>
        <div class="p-5 space-y-4">
          <div class="rounded-lg border border-gray-200 p-3 space-y-2">
            <div class="font-semibold text-sm">Presenter</div>
            <input v-model.trim="addForm.presenter_name" type="text" class="field-input" placeholder="Presenter name (required)" />
            <input v-model.trim="addForm.title" type="text" class="field-input" placeholder="Presentation / session title (optional)" />
          </div>

          <div class="rounded-lg border border-gray-200 p-3 space-y-2">
            <div class="font-semibold text-sm">Schedule</div>
            <div class="grid grid-cols-2 gap-2">
              <div>
                <label class="text-[11px] font-semibold text-gray-500 block mb-1">Category</label>
                <select v-model="addForm.category" class="field-input">
                  <option value="oral">Abstract (Oral)</option>
                  <option value="poster">Poster</option>
                </select>
              </div>
              <div>
                <label class="text-[11px] font-semibold text-gray-500 block mb-1">Day</label>
                <select v-model="addForm.day" class="field-input">
                  <option v-for="d in addDayOptions" :key="d" :value="d">{{ d }}</option>
                </select>
              </div>
            </div>
            <div>
              <label class="text-[11px] font-semibold text-gray-500 block mb-1">Room</label>
              <input v-model.trim="addForm.room" type="text" list="add-room-options"
                class="field-input" placeholder="Type a room name or pick one…" />
              <datalist id="add-room-options">
                <option v-for="r in addRoomOptions" :key="r" :value="r">{{ r }}</option>
              </datalist>
            </div>
            <div>
              <label class="text-[11px] font-semibold text-gray-500 block mb-1">Session (optional)</label>
              <input v-model.trim="addForm.session" type="text" class="field-input" placeholder="e.g. S03" />
            </div>
          </div>

          <!-- Slides -->
          <div class="rounded-lg border border-gray-200 p-3 space-y-2">
            <div class="font-semibold text-sm">Slides</div>
            <div v-if="addFile" class="flex items-center justify-between gap-2 text-sm text-gray-600">
              <span class="truncate text-teal-600 font-medium">✓ {{ addFile.name }}</span>
              <button @click="removeAddFile" class="text-red-500 font-medium hover:underline flex-shrink-0">Remove</button>
            </div>
            <div v-else>
              <button @click="triggerAddUpload" class="px-3 py-1.5 text-xs font-semibold rounded-full border"
                style="border-color: rgb(0,150,180); color: rgb(0,150,180);">
                Attach presentation (PDF / PPTX / image)
              </button>
              <p class="text-[11px] text-gray-400 mt-1.5">Optional — you can also attach slides later via the pencil icon on the entry.</p>
            </div>
          </div>
          <div v-if="addErr" class="px-3 py-2 rounded-md bg-red-50 text-red-600 text-sm">{{ addErr }}</div>
        </div>
        <div class="px-5 py-4 border-t border-gray-100 flex justify-end gap-2">
          <button @click="closeAdd" class="px-4 py-2 text-sm font-medium text-gray-600 hover:bg-gray-50 rounded-lg">Cancel</button>
          <button @click="saveAdd" :disabled="addBusy || !addForm.presenter_name.trim()"
            class="px-4 py-2 text-sm font-semibold text-white rounded-lg disabled:opacity-50"
            style="background-color: rgb(16,150,60);">
            {{ addBusy ? 'Saving…' : (addFile ? 'Add Presenter & Attach Slides' : 'Add Presenter') }}
          </button>
        </div>
      </div>
    </div>

    <!-- Manage entry modal -->
    <div v-if="manageOpen" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/40" @click.self="closeManage">
      <div class="bg-white rounded-xl shadow-xl w-full max-w-lg max-h-[90vh] overflow-y-auto">
        <div class="px-5 py-4 border-b border-gray-100 flex items-center justify-between">
          <div>
            <div class="font-bold">{{ manageTarget.is_substitution ? 'Substitute Presenter' : 'Manage Presentation' }}</div>
            <div class="text-xs text-gray-500">{{ manageTarget.code || manageTarget.category }} · {{ manageTarget.room }} · {{ manageTarget.day }}</div>
          </div>
          <button @click="closeManage" class="text-gray-400 hover:text-gray-600">
            <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" d="M6 18L18 6M6 6l12 12"/></svg>
          </button>
        </div>
        <div class="p-5 space-y-4">
          <!-- Replace / add presenter -->
          <div class="rounded-lg border border-gray-200 p-3 space-y-2">
            <div class="font-semibold text-sm">Presenter</div>
            <input v-model.trim="manageForm.presenter_name" type="text" class="field-input" placeholder="Presenter name" />
            <label class="flex items-center gap-2 text-sm font-medium cursor-pointer">
              <input type="checkbox" v-model="manageForm.is_substitution" class="accent-amber-600" />
              Substitute presenting instead of
            </label>
            <input v-if="manageForm.is_substitution" v-model.trim="manageForm.original_presenter" type="text"
              class="field-input" placeholder="Original (absent) presenter" />
          </div>
          <!-- Slides -->
          <div class="rounded-lg border border-gray-200 p-3 space-y-2">
            <div class="font-semibold text-sm">Slides</div>
            <div v-if="manageTarget.presentation_file" class="flex items-center gap-2 text-sm text-gray-600">
              <span class="text-teal-600 font-medium">✓ uploaded</span>
              <button @click="downloadSingle(manageTarget)" class="text-cp-secondary font-medium hover:underline">re-download</button>
            </div>
            <div class="flex flex-wrap gap-2">
              <button @click="triggerUpload" class="px-3 py-1.5 text-xs font-semibold rounded-full border"
                style="border-color: rgb(0,150,180); color: rgb(0,150,180);">
                {{ manageTarget.presentation_file ? 'Replace slides' : 'Upload slides' }}
              </button>
              <a v-if="manageTarget.presentation_file" @click.prevent="removeSlides"
                class="px-3 py-1.5 text-xs font-semibold rounded-full border border-red-200 text-red-600 hover:bg-red-50 cursor-pointer">
                Remove slides
              </a>
            </div>
          </div>
          <!-- Video link -->
          <div class="rounded-lg border border-gray-200 p-3 space-y-2">
            <div class="font-semibold text-sm">Video link</div>
            <p class="text-xs text-gray-500">For a recording or a video-embedded deck too large to upload — paste a YouTube (can be unlisted), Vimeo, or Google Drive share link instead. Shows as a "Watch video" button on the room page.</p>
            <input v-model.trim="manageForm.video_url" type="url" class="field-input" placeholder="https://youtu.be/… or https://drive.google.com/…" />
          </div>
          <div v-if="manageErr" class="px-3 py-2 rounded-md bg-red-50 text-red-600 text-sm">{{ manageErr }}</div>
        </div>
        <div class="px-5 py-4 border-t border-gray-100 flex justify-end gap-2">
          <button @click="closeManage" class="px-4 py-2 text-sm font-medium text-gray-600 hover:bg-gray-50 rounded-lg">Cancel</button>
          <button @click="saveManage" :disabled="manageBusy" class="px-4 py-2 text-sm font-semibold text-white rounded-lg"
            style="background-color: rgb(254,80,103);">Save</button>
        </div>
      </div>
    </div>

    <!-- Slides preview modal (mirror of PdfPreviewModal) -->
    <div v-if="preview.open" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60" @click.self="preview.open = false">
      <div class="bg-white rounded-xl shadow-xl w-full max-w-3xl h-[85vh] flex flex-col">
        <div class="px-4 py-3 border-b border-gray-100 flex items-center justify-between">
          <div class="font-semibold text-sm truncate pr-4">{{ preview.name }}</div>
          <div class="flex items-center gap-2">
            <button v-if="preview.entry" @click="downloadSingle(preview.entry)"
              class="inline-flex items-center gap-1 px-3 py-1.5 text-xs font-semibold rounded-full text-white"
              style="background-color: rgb(0,150,180);">
              <svg class="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                <path stroke-linecap="round" stroke-linejoin="round" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"/>
              </svg>
              Download
            </button>
            <button @click="preview.open = false" class="text-gray-400 hover:text-gray-600">
              <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" d="M6 18L18 6M6 6l12 12"/></svg>
            </button>
          </div>
        </div>
        <div class="flex-1 bg-gray-100 min-h-0">
          <iframe :src="preview.src" class="w-full h-full border-0" title="Slides preview"></iframe>
        </div>
      </div>
    </div>

    <input type="file" ref="slideInput" class="hidden" :accept="acceptedExtensions" @change="onSlideSelected" />
    <input type="file" ref="addSlideInput" class="hidden" :accept="acceptedExtensions" @change="onAddSlideSelected" />

    <!-- Off-screen PDF template for the per-room presenter-list export
    (parked far off-window so it's never visible) -->
    <div ref="pdfNode" id="roomPdfNode" style="position:absolute; left:-9999px; top:0; width:794px;" aria-hidden="true"></div>

    <!-- Batch ZIP download progress overlay -->
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

    <!-- Bulk file matcher modal -->
    <div v-if="bulkOpen" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/40" @click.self="closeBulkUpload">
      <div class="bg-white rounded-xl shadow-xl w-full max-w-4xl max-h-[90vh] flex flex-col">
        <div class="px-5 py-4 border-b border-gray-100 flex items-center justify-between flex-shrink-0">
          <div>
            <h3 class="font-bold text-gray-800">Bulk Match & Upload Presentations</h3>
            <p class="text-xs text-gray-500 mt-0.5">Pick every file from a folder at once — each gets matched to a programme entry by abstract code or presenter name. Review the guesses, fix any that are wrong, then upload.</p>
          </div>
          <button @click="closeBulkUpload" :disabled="bulkBusy" class="text-gray-400 hover:text-gray-600 disabled:opacity-40">
            <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" d="M6 18L18 6M6 6l12 12"/></svg>
          </button>
        </div>

        <div class="px-5 py-4 overflow-y-auto flex-1 space-y-4">
          <div v-if="bulkTargetsLoading" class="py-10"><SpinnerComponent /></div>
          <div v-else-if="bulkTargetsErr" class="px-3 py-2 rounded-md bg-red-50 text-red-600 text-sm">{{ bulkTargetsErr }}</div>
          <template v-else>
            <div class="flex flex-wrap items-center gap-3">
              <button @click="$refs.bulkFileInput.click()" :disabled="bulkBusy"
                class="inline-flex items-center gap-1.5 px-4 py-2 rounded-lg text-sm font-semibold text-white disabled:opacity-50"
                style="background-color: rgb(120,80,200);">
                <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M12 4v16m8-8H4"/>
                </svg>
                Choose Files…
              </button>
              <span class="text-xs text-gray-500">Select every file at once (⌘/Ctrl-click or Ctrl/Cmd-A in the picker) — PDF, PPTX, images, or video (MP4/MOV).</span>
            </div>

            <div v-if="bulkRows.length === 0" class="py-10 text-center text-sm text-gray-400 italic border border-dashed border-gray-200 rounded-lg">
              No files chosen yet.
            </div>

            <div v-else class="rounded-lg border border-gray-200 divide-y divide-gray-100">
              <div v-for="(row, i) in bulkRows" :key="i" class="px-4 py-3 flex flex-col gap-2">
                <div class="flex items-start gap-3">
                  <input type="checkbox" v-model="row.include" :disabled="bulkBusy || row.tooLarge" class="mt-1.5 accent-cp-secondary flex-shrink-0" />
                  <div class="flex-1 min-w-0">
                    <div class="flex flex-wrap items-center gap-x-2 gap-y-0.5">
                      <span class="font-semibold text-sm truncate" :class="row.tooLarge ? 'text-gray-400' : ''">{{ row.name }}</span>
                      <span class="text-[11px] text-gray-400">{{ row.sizeLabel }}</span>
                      <span v-if="row.tooLarge" class="text-[10px] font-semibold px-1.5 py-0.5 rounded uppercase bg-red-100 text-red-700">Too large</span>
                      <span v-else class="text-[10px] font-semibold px-1.5 py-0.5 rounded uppercase" :class="bulkConfidenceClass(row.confidence)">
                        {{ bulkConfidenceLabel(row.confidence) }}
                      </span>
                      <span v-if="row.status === 'uploading'" class="text-[11px] font-semibold text-blue-600">Uploading… {{ row.progress }}%</span>
                      <span v-if="row.status === 'done'" class="text-[11px] font-semibold text-green-600">✓ Uploaded</span>
                      <span v-if="row.status === 'error'" class="text-[11px] font-semibold text-red-600">{{ row.error }}</span>
                    </div>
                    <p v-if="row.tooLarge" class="text-[11px] text-red-600 mt-1">
                      Over 95MB — our CDN (Cloudflare) rejects uploads past ~100MB no matter how long you wait, this can't go through this tool.
                      Upload it to YouTube (unlisted) or Google Drive, then paste the link on this entry's <strong>Video link</strong> field (pencil icon on the room card) instead.
                    </p>
                    <template v-else>
                      <input v-model="row.pickText" @input="resolveBulkPick(row)" list="bulkEntryOptions"
                        :disabled="bulkBusy || row.status === 'done'"
                        placeholder="Type presenter name, code, or title to search the programme…"
                        class="field-input !py-1.5 !text-xs mt-1 w-full disabled:bg-gray-50 disabled:text-gray-400" />
                      <div v-if="row.status === 'uploading'" class="h-1.5 w-full bg-gray-100 rounded-full overflow-hidden mt-1.5">
                        <div class="h-full rounded-full transition-all duration-150" :style="{ width: row.progress + '%', backgroundColor: 'rgb(120,80,200)' }"></div>
                      </div>
                      <p v-if="row.include && !row.entryId" class="text-[11px] text-amber-600 mt-1">No entry chosen yet — pick one above or untick to skip this file.</p>
                    </template>
                  </div>
                  <button v-if="row.status !== 'done'" @click="removeBulkRow(row)" :disabled="bulkBusy" title="Remove"
                    class="text-gray-300 hover:text-red-500 flex-shrink-0 disabled:opacity-40">
                    <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" d="M6 18L18 6M6 6l12 12"/></svg>
                  </button>
                </div>
              </div>
            </div>
            <datalist id="bulkEntryOptions">
              <option v-for="o in bulkDatalistOptions" :key="o.id" :value="o.label" />
            </datalist>

            <div v-if="bulkUnresolvedCount > 0" class="text-xs text-amber-600">
              {{ bulkUnresolvedCount }} selected file{{ bulkUnresolvedCount !== 1 ? 's' : '' }} still need{{ bulkUnresolvedCount === 1 ? 's' : '' }} a matching entry before they can upload.
            </div>
            <div v-if="bulkErr" class="px-3 py-2 rounded-md bg-red-50 text-red-600 text-sm">{{ bulkErr }}</div>

            <!-- Programme-wide status — separate from whatever's in the file
            picker above, so the admin can see overall progress at a glance. -->
            <div class="border-t border-gray-100 pt-3 space-y-2">
              <button type="button" @click="bulkShowNotUploaded = !bulkShowNotUploaded"
                class="w-full flex items-center justify-between px-3 py-2 rounded-lg bg-amber-50 hover:bg-amber-100 transition">
                <span class="text-xs font-bold text-amber-700">Not uploaded yet ({{ bulkNotUploadedTargets.length }})</span>
                <svg class="w-4 h-4 text-amber-600 transition-transform" :class="bulkShowNotUploaded ? 'rotate-180' : ''" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M19 9l-7 7-7-7"/>
                </svg>
              </button>
              <div v-if="bulkShowNotUploaded" class="rounded-lg border border-gray-200 divide-y divide-gray-100 max-h-56 overflow-y-auto">
                <div v-if="bulkNotUploadedTargets.length === 0" class="px-4 py-4 text-center text-xs text-gray-400 italic">Everything has a file or video link. 🎉</div>
                <div v-for="t in bulkNotUploadedTargets" :key="t.id" class="px-3 py-2 text-xs text-gray-600">
                  {{ t.label }}
                </div>
              </div>

              <button type="button" @click="bulkShowUploaded = !bulkShowUploaded"
                class="w-full flex items-center justify-between px-3 py-2 rounded-lg bg-green-50 hover:bg-green-100 transition">
                <span class="text-xs font-bold text-green-700">Already uploaded ({{ bulkUploadedTargets.length }})</span>
                <svg class="w-4 h-4 text-green-600 transition-transform" :class="bulkShowUploaded ? 'rotate-180' : ''" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M19 9l-7 7-7-7"/>
                </svg>
              </button>
              <div v-if="bulkShowUploaded" class="rounded-lg border border-gray-200 divide-y divide-gray-100 max-h-56 overflow-y-auto">
                <div v-if="bulkUploadedTargets.length === 0" class="px-4 py-4 text-center text-xs text-gray-400 italic">Nothing uploaded yet.</div>
                <div v-for="t in bulkUploadedTargets" :key="t.id" class="px-3 py-2 text-xs text-gray-600 flex items-center justify-between gap-2">
                  <span class="truncate">{{ t.label }}</span>
                  <span class="flex-shrink-0 text-[10px] font-semibold px-1.5 py-0.5 rounded uppercase"
                    :class="t.has_presentation ? 'bg-teal-100 text-teal-700' : 'bg-purple-100 text-purple-700'">
                    {{ t.has_presentation ? 'File' : 'Video' }}
                  </span>
                </div>
              </div>
            </div>
          </template>
        </div>

        <div class="px-5 py-3 border-t border-gray-100 flex-shrink-0 bg-white">
          <div v-if="bulkBusy" class="mb-2.5">
            <div class="flex items-center justify-between text-xs text-gray-600 mb-1">
              <span>Uploading file {{ bulkProgress.done + 1 > bulkProgress.total ? bulkProgress.total : bulkProgress.done + 1 }} of {{ bulkProgress.total }} — {{ formatFileSize(bulkProgress.sentBytes) }} of {{ formatFileSize(bulkProgress.totalBytes) }}</span>
              <span class="font-bold">{{ bulkProgress.percent }}%</span>
            </div>
            <div class="h-2 w-full bg-gray-100 rounded-full overflow-hidden">
              <div class="h-full rounded-full transition-all duration-150" :style="{ width: bulkProgress.percent + '%', backgroundColor: 'rgb(120,80,200)' }"></div>
            </div>
          </div>
          <div class="flex items-center justify-between gap-3">
            <div class="text-xs text-gray-500">
              <template v-if="!bulkBusy && bulkIncludedCount">{{ bulkIncludedCount }} file{{ bulkIncludedCount !== 1 ? 's' : '' }} ready to upload</template>
            </div>
            <div class="flex gap-2">
              <button @click="closeBulkUpload" :disabled="bulkBusy" class="px-4 py-2 text-sm font-medium text-gray-600 hover:bg-gray-50 rounded-lg disabled:opacity-40">Close</button>
              <button @click="runBulkUpload" :disabled="bulkBusy || bulkIncludedCount === 0"
                class="px-4 py-2 text-sm font-semibold text-white rounded-lg disabled:opacity-50"
                style="background-color: rgb(120,80,200);">
                {{ bulkBusy ? `Uploading… ${bulkProgress.percent}%` : `Upload ${bulkIncludedCount} File${bulkIncludedCount !== 1 ? 's' : ''}` }}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <input type="file" ref="bulkFileInput" class="hidden" multiple :accept="bulkAcceptedExtensions" @change="onBulkFilesChosen" />
  </div>
</template>

<script>
import HeaderView from '@/includes/Header.vue'
import SpinnerComponent from '@/components/Spinner.vue'
import { useAuthStore } from '@/store/authStore'
import { saveAs } from 'file-saver'
import axios from 'axios'
// Inlined as data URLs so html2canvas can always render them (no CORS /
// asset-path worries), the same way badges embed the crest + brand mark.
import ecsaCrest from '@/assets/images/ecsalogo.png?inline'
import ecsaconmMark from '@/assets/images/logo.png?inline'

const DAY_ORDER = ['Day 1', 'Day 2', 'Day 3', 'Day 1-3', 'Unassigned']

// ── Bulk file matcher helpers ─────────────────────────────────────────────
// Pure string-matching used to line a folder of local presentation files up
// against programme entries before upload. Runs entirely client-side — the
// files themselves never leave the browser until the admin confirms a match
// and clicks Upload, one authenticated POST per file, same as a manual
// single-file upload would do.
const BULK_STOPWORDS = new Set([
  'ecsaconm', 'ecsacon', 'conference', 'presentation', 'presentations', 'present',
  'final', 'fin', 'draft', 'rev', 'revised', 'ppt', 'pptx', 'pdf', 'poster',
  'oral', 'abstract', 'sept', 'september', '2025', '2026', 'the', 'a', 'an',
  'of', 'and', 'for', 'to', 'on', 'in', 'at', 'dr', 'prof', 'professor', 'mr',
  'mrs', 'ms', 'phd', 'rn', 'rm', 'msc', 'bsc', 'copy', 'new',
])
const BULK_CODE_RE = /\b(HAE|RIN|LAP|TECH|CLIM|ID)-?0*(\d{1,4})\b/i
// Production runs behind Cloudflare's proxy, which hard-caps request bodies
// at 100MB (confirmed directly: a 150MB test upload got an instant 413 from
// Cloudflare itself, never even reaching nginx) — no server-side setting can
// raise this. A file over this line will never succeed through this tool no
// matter how long it "uploads" for, so it's refused client-side up front
// with a pointer to the Video link field instead of hanging.
const BULK_MAX_UPLOAD_BYTES = 95 * 1024 * 1024

function bulkNorm(s) {
  return (s || '')
    .toString()
    .normalize('NFKD').replace(/[̀-ͯ]/g, '')
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, ' ')
    .trim()
}
function bulkTokens(s) {
  return bulkNorm(s).split(' ').filter(t => t.length > 1 && !BULK_STOPWORDS.has(t))
}
function bulkExtractCode(filename) {
  const m = (filename || '').match(BULK_CODE_RE)
  if (!m) return null
  return `${m[1].toUpperCase()}${m[2].padStart(3, '0')}`
}
// Ranks every candidate entry against one filename and returns the best
// guess plus a confidence label. Never auto-selects on its own — the caller
// always shows this as an editable, overridable suggestion.
function bulkBestMatch(filename, targets) {
  const stem = filename.replace(/\.[a-z0-9]+$/i, '')
  const code = bulkExtractCode(stem)
  if (code) {
    const hit = targets.find(t => (t.code || '').toUpperCase() === code)
    if (hit) return { entry: hit, confidence: 'high', reason: `code ${code}` }
  }
  const fileTokens = new Set(bulkTokens(stem))
  if (fileTokens.size === 0) return { entry: null, confidence: 'none', reason: '' }
  let best = null
  let bestScore = 0
  let bestNameHits = 0
  for (const t of targets) {
    const nameTokens = bulkTokens(t.presenter_name)
    const titleTokens = bulkTokens(t.title || t.activity || '')
    let nameHits = 0
    for (const tok of nameTokens) if (fileTokens.has(tok)) nameHits++
    let titleHits = 0
    for (const tok of titleTokens) if (fileTokens.has(tok)) titleHits++
    const score = nameHits * 3 + titleHits
    if (score > bestScore) {
      bestScore = score
      best = t
      bestNameHits = nameHits
    }
  }
  if (!best) return { entry: null, confidence: 'none', reason: '' }
  if (bestNameHits >= 2) return { entry: best, confidence: 'medium', reason: 'name match' }
  if (bestNameHits === 1 && bestScore >= 4) return { entry: best, confidence: 'low', reason: 'partial name + title match' }
  if (bestNameHits === 1) return { entry: best, confidence: 'low', reason: 'weak name match' }
  return { entry: null, confidence: 'none', reason: '' }
}
function bulkEntryLabel(t) {
  const cat = t.category === 'plenary' ? 'Plenary' : t.category === 'poster' ? 'Poster' : 'Oral'
  const code = t.code ? `${t.code} · ` : ''
  const where = [t.day, t.room].filter(Boolean).join(' · ')
  const what = (t.title || t.activity || '').slice(0, 70)
  return `#${t.id} · ${cat} · ${code}${t.presenter_name || '—'} — ${what}${where ? ` (${where})` : ''}`
}

export default {
  name: 'ProgrammeRoomsView',
  components: { HeaderView, SpinnerComponent },

  data() {
    return {
      roomsData: [],
      loading: false,
      activeRoom: 'All Rooms',
      activeDay: 'All Days',
      showPastDays: false,
      eventStartDate: null,
      eventEndDate: null,
      entryCategory: 'oral',
      categoryOptions: [
        { key: 'oral', label: 'Abstracts' },
        { key: 'poster', label: 'Posters' },
        { key: 'plenary', label: 'Plenary' },
      ],
      apiUrl: import.meta.env.VITE_API_URL,
      flashMsg: '', flashErr: false,
      addOpen: false, addBusy: false, addErr: '', addFile: null,
      addForm: { presenter_name: '', title: '', category: 'oral', day: 'Day 1', room: '', session: '' },
      manageOpen: false, manageTarget: null, manageForm: {}, manageBusy: false, manageErr: '',
      preview: { open: false, name: '', src: '', entry: null },
      zipBusy: false,
      pdfBusy: null,
      zipProgress: { active: false, room: '', percent: 0, loadedMB: '0.0', totalMB: null },
      roomDeleting: null,
      entryDeleting: null,
      backfillBusy: false,
      matchOpen: false, matchLoading: false, matchReport: null, matchErr: '',
      matchApplying: false, matchApplyResult: null, matchSelected: {},
      linkChoice: {}, linkBusy: false,
      acceptedExtensions: '.pdf,.pptx,.jpg,.jpeg,.png,.gif,.bmp,.webp',
      // assign presenters state
      assignOpen: false, assignLoading: false, assignRows: [], assignCategory: 'all',
      assignSearch: '',
      assignErr: '', assignDone: null, assignBusy: false, assignSelected: {},
      assignForm: { room: '', day: 'Day 2' },
      // bulk file matcher state
      bulkOpen: false, bulkTargetsLoading: false, bulkTargets: [], bulkTargetsErr: '',
      bulkRows: [], bulkBusy: false, bulkProgress: { done: 0, total: 0 }, bulkErr: '',
      bulkAcceptedExtensions: '.pdf,.pptx,.jpg,.jpeg,.png,.gif,.bmp,.webp,.mp4,.mov,.m4v,.webm',
      bulkShowUploaded: false, bulkShowNotUploaded: true,
    }
  },

  setup() {
    const authStore = useAuthStore()
    return { accessToken: authStore.accessToken, isAdmin: authStore.permissions?.some(p => (typeof p === 'string' ? p : p.permission_code) === 'ADMIN_DASHBOARD') }
  },

  computed: {
    // roomsData buckets mix every category together (plenary/oral/poster) —
    // this page is scoped to abstracts (oral) and posters only, one at a
    // time, so every other computed below filters through this first.
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
      // keep a stable order
      const all = [...rooms]
      return all.sort((a, b) => (a === 'All Rooms' ? -1 : b === 'All Rooms' ? 1 : a.localeCompare(b)))
    },
    // Every day that currently has data, in DAY_ORDER, each flagged with
    // whether its calendar date has already passed (unaffected by the day
    // filter/past-day toggle — those apply on top, in roomDays below).
    // Filtered by the active room selection, so it drives what actually
    // renders as room cards.
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
    // Every day that has data across ALL rooms, ignoring the active room
    // filter — the day chip row and the "N past days" toggle should stay
    // stable no matter which room is currently selected, otherwise picking
    // a room can make a day chip disappear just because that particular
    // room has no entries on it, which reads as the filter randomly hiding
    // days.
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
    // What actually renders: allRoomDays narrowed by the day filter and by
    // the past-days toggle (past days hidden by default).
    roomDays() {
      return this.allRoomDays.filter(d => {
        if (!this.showPastDays && d.isPast) return false
        if (this.activeDay !== 'All Days' && d.day !== this.activeDay) return false
        return true
      })
    },
    slideCountSummary() {
      const total = this.categoryRoomsData.reduce((s, d) => s + d.entries.length, 0)
      const withSlide = this.categoryRoomsData.reduce((s, d) => s + d.entries.filter(e => e.has_presentation).length, 0)
      return `${withSlide} of ${total} presentations have slides`
    },
    selectedMatchCount() {
      return Object.values(this.matchSelected).filter(Boolean).length
    },
    assignDays() {
      // Every single conference day is offered regardless of whether it
      // already has room entries — rooms can be freeform-typed in step 2.
      return DAY_ORDER.filter(day => /^Day \d+$/.test(day))
    },
    assignRoomsForDay() {
      return this.roomsData
        .filter(d => d.day === this.assignForm.day && d.room)
        .map(d => ({ room: d.room, total: d.total, with_slide: d.with_slide }))
        .sort((a, b) => a.room.localeCompare(b.room))
    },
    assignFilteredRows() {
      const q = (this.assignSearch || '').trim().toLowerCase()
      let rows = this.assignRows
      if (this.assignCategory !== 'all') {
        rows = rows.filter(r => (r.presentation_type || 'oral') === this.assignCategory)
      }
      if (q) {
        rows = rows.filter(r =>
          (r.presenter || '').toLowerCase().includes(q) ||
          (r.title || '').toLowerCase().includes(q)
        )
      }
      return rows
    },
    assignSelectedCount() {
      const rows = this.assignFilteredRows
      return rows.filter(r => this.assignSelected[r.abstract_id]).length
    },
    assignCategoryOptions() {
      const by = { oral: 0, poster: 0 }
      for (const r of this.assignRows) {
        const t = r.presentation_type || 'oral'
        if (t in by) by[t]++
      }
      return [
        { key: 'all', label: 'All', count: this.assignRows.length },
        { key: 'oral', label: 'Oral', count: by.oral },
        { key: 'poster', label: 'Poster', count: by.poster },
      ]
    },
    // Manual-add modal: every conference day is offered (rooms page never
    // auto-creates buckets for empty days), defaulting to the day currently
    // filtered so the new entry lands where the admin is looking.
    addDayOptions() {
      return DAY_ORDER
    },
    // Existing room names for the selected day — shown as suggestions so the
    // admin reuses the exact room string (matching matters: "GTCC 1" is not
    // "gtcc 1"), but they can still type a brand-new room.
    addRoomOptions() {
      const rooms = new Set()
      for (const d of this.roomsData) {
        if (d.day !== this.addForm.day || !d.room) continue
        rooms.add(d.room)
      }
      return [...rooms].sort((a, b) => a.localeCompare(b))
    },

    // ── bulk file matcher ──────────────────────────────────────
    bulkDatalistOptions() {
      return this.bulkTargets.map(t => ({ id: t.id, label: bulkEntryLabel(t) }))
    },
    bulkIncludedCount() {
      return this.bulkRows.filter(r => r.include && r.entryId).length
    },
    bulkUnresolvedCount() {
      return this.bulkRows.filter(r => r.include && !r.entryId).length
    },
    // Status of the whole programme, independent of whatever's in the file
    // picker right now — lets the admin see overall progress (and who's
    // still missing something) without leaving the modal. Reactive to
    // uploads that just completed, since runBulkUpload patches bulkTargets
    // in place as each one finishes.
    bulkUploadedTargets() {
      return this.bulkTargets.filter(t => t.has_presentation || t.video_url).map(t => ({ ...t, label: bulkEntryLabel(t) }))
    },
    bulkNotUploadedTargets() {
      return this.bulkTargets.filter(t => !t.has_presentation && !t.video_url).map(t => ({ ...t, label: bulkEntryLabel(t) }))
    },
  },

  watch: {
    // Room chips are category-specific (e.g. "Poster Area" only exists for
    // posters) — a stale pick from the other category would just show
    // nothing, so reset it whenever the category switches.
    entryCategory() {
      this.activeRoom = 'All Rooms'
      this.activeDay = 'All Days'
    },
  },

  mounted() {
    this.loadRooms()
  },

  methods: {
    async loadRooms() {
      this.loading = true
      try {
        const res = await axios.get(`${this.apiUrl}/programme/rooms`, {
          params: { event_id: 1 },
          headers: { Authorization: `Bearer ${this.accessToken}` },
        })
        this.roomsData = res.data.data || []
        this.eventStartDate = res.data.event_start_date || null
        this.eventEndDate = res.data.event_end_date || null
      } catch (e) {
        this.flash('Failed to load rooms.', true)
      } finally {
        this.loading = false
      }
    },

    // ── slides ────────────────────────────────────────────────
    // entry.presentation_ext (from the backend) already accounts for the
    // linked-abstract fallback — don't parse entry.presentation_file, it's
    // only ever the entry's own upload and is null when the file being
    // served actually came from the abstract.
    isPreviewable(ext) {
      const e = (ext || '').replace(/^\./, '').toLowerCase()
      return ['pdf', 'pptx', 'jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp'].includes(e)
    },
    previewSrc(entry) {
      const ext = (entry.presentation_ext || '').replace(/^\./, '').toLowerCase()
      const fileUrl = `${this.apiUrl}/programme/${entry.id}/preview-presentation`
      return ['pdf', 'jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp'].includes(ext)
        ? fileUrl
        : `https://view.officeapps.live.com/op/embed.aspx?src=${encodeURIComponent(fileUrl)}`
    },
    openPreview(entry) {
      if (!this.isPreviewable(entry.presentation_ext)) {
        this.flash('Preview not supported for this file type — use Download instead.', true)
        return
      }
      this.preview = { open: true, name: entry.title || entry.presenter_name, src: this.previewSrc(entry), entry }
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
        const blob = e.response?.data
        if (blob instanceof Blob) {
          try { this.flash(JSON.parse(await blob.text())?.detail || 'Download failed.', true) }
          catch { this.flash('Download failed.', true) }
        } else {
          this.flash(e.response?.data?.detail || 'Download failed.', true)
        }
      }
    },

    async downloadRoomZip(room) {
      this.zipBusy = true
      this.zipProgress = { active: true, room: room.room || 'All Rooms', percent: 0, loadedMB: '0.0', totalMB: null }
      try {
        const res = await axios.get(`${this.apiUrl}/programme/download-room-zip`, {
          params: { event_id: 1, room: room.room, day: room.day },
          responseType: 'blob',
          onDownloadProgress: (evt) => {
            this.zipProgress.loadedMB = (evt.loaded / 1048576).toFixed(1)
            // evt.total is only known if the server sends Content-Length —
            // falls back to just the running MB count otherwise.
            if (evt.total) {
              this.zipProgress.totalMB = (evt.total / 1048576).toFixed(1)
              this.zipProgress.percent = Math.round((evt.loaded / evt.total) * 100)
            }
          },
        })
        saveAs(res.data, `room_${(room.room || 'all').replace(/[^A-Za-z0-9_]+/g, '_')}.zip`)
      } catch (e) {
        const blob = e.response?.data
        if (blob instanceof Blob) {
          try { this.flash(JSON.parse(await blob.text())?.detail || 'No slides to download.', true) }
          catch { this.flash('No slides to download for this room.', true) }
        } else {
          this.flash(e.response?.data?.detail || 'Download failed.', true)
        }
      } finally {
        this.zipBusy = false
        this.zipProgress.active = false
      }
    },

    async deleteRoom(room) {
      // The backend deletes by room name across every day (a room isn't a
      // per-day thing) — so total the count across all day-buckets sharing
      // this exact room name, not just the one card that was clicked.
      const totalAcrossDays = this.roomsData
        .filter(d => d.room === room.room)
        .reduce((s, d) => s + d.total, 0)
      if (!confirm(`Delete every entry in room "${room.room}" — across all days, ${totalAcrossDays} presentation${totalAcrossDays !== 1 ? 's' : ''} total? This removes them from the programme entirely, not just unassigning them. This cannot be undone.`)) return
      this.roomDeleting = room.room
      try {
        const res = await axios.delete(`${this.apiUrl}/programme/room`, {
          params: { event_id: 1, room: room.room },
          headers: { Authorization: `Bearer ${this.accessToken}` },
        })
        this.flash(res.data?.detail || 'Room deleted.', false)
        await this.loadRooms()
      } catch (e) {
        this.flash(e.response?.data?.detail || 'Failed to delete room.', true)
      } finally {
        this.roomDeleting = null
      }
    },

    async deleteEntry(entry) {
      const who = entry.presenter_name || 'this presenter'
      const what = entry.title || entry.activity || 'this entry'
      if (!confirm(`Delete "${what}" (${who})? This removes just this one entry — nothing else in this room or day is affected. This cannot be undone.`)) return
      this.entryDeleting = entry.id
      try {
        await axios.delete(`${this.apiUrl}/programme/${entry.id}`, {
          headers: { Authorization: `Bearer ${this.accessToken}` },
        })
        this.flash('Entry deleted.', false)
        await this.loadRooms()
      } catch (e) {
        this.flash(e.response?.data?.detail || 'Failed to delete entry.', true)
      } finally {
        this.entryDeleting = null
      }
    },

    roomShareUrl(room) {
      const params = new URLSearchParams({ event_id: '1', day: room.day, room: room.room })
      return `${window.location.origin}${window.location.pathname}#/room-programme?${params.toString()}`
    },
    async copyRoomLink(room) {
      const url = this.roomShareUrl(room)
      try {
        await navigator.clipboard.writeText(url)
        this.flash('Link copied — share it with this room\'s leader.')
      } catch (e) {
        // clipboard API can be unavailable (older browsers, non-HTTPS) —
        // fall back to just showing it so it can be selected and copied.
        window.prompt('Copy this link:', url)
      }
    },
    async copyPublicProgrammeLink() {
      const url = `${window.location.origin}${window.location.pathname}#/programme-rooms-public?event_id=1`
      try {
        await navigator.clipboard.writeText(url)
        this.flash('Link copied — view-only, no login required, every room and day.')
      } catch (e) {
        window.prompt('Copy this link:', url)
      }
    },

    // Fills in the room for every entry currently sitting in the
    // "Unassigned" bucket, matched by abstract code against
    // PROGRAMME_ROOM_GUIDANCE (transcribed from the official conference
    // programme PDF) — never touches an entry that already has a room.
    async runBackfillRooms() {
      if (this.backfillBusy) return
      if (!confirm('Fill in rooms for every Unassigned entry, matched by code against the official programme? Entries that already have a room are never touched.')) return
      this.backfillBusy = true
      try {
        const res = await axios.post(`${this.apiUrl}/programme/backfill-rooms`, null, {
          params: { event_id: 1 },
          headers: { Authorization: `Bearer ${this.accessToken}` },
        })
        const { updated_count, not_found_count } = res.data
        this.flash(
          `Filled in ${updated_count} room${updated_count === 1 ? '' : 's'}.` +
          (not_found_count ? ` ${not_found_count} entr${not_found_count === 1 ? 'y has' : 'ies have'} no matching code in the programme — still Unassigned.` : ''),
          false,
        )
        await this.loadRooms()
      } catch (e) {
        this.flash(e.response?.data?.detail || 'Failed to fill in rooms.', true)
      } finally {
        this.backfillBusy = false
      }
    },

    // ── per-room PDF export ─────────────────────────────────
    escHtml(s) {
      return String(s ?? '').replace(/[&<>"']/g, c => (
        { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]
      ))
    },
    // Rebuilds the off-screen template for the given day/room bucket so the
    // snapshot matches exactly what's shown on that room card right now.
    buildRoomPdfHtml(room) {
      const esc = this.escHtml
      const rows = room.entries.map((e, i) => {
        const sub = e.is_substitution
          ? `<span style="font-size:9px;background:#fef3c7;color:#b45309;border:1px solid #fbbf24;border-radius:3px;padding:0 4px;margin-left:5px;font-weight:700;">SUB</span>`
            + (e.original_presenter ? `<span style="font-size:10px;color:#6b7280;margin-left:4px;">for ${esc(e.original_presenter)}</span>` : '')
          : ''
        const poster = e.category === 'poster'
          ? ` <span style="font-size:9px;background:#fef3c7;color:#b45309;border:1px solid #fbbf24;border-radius:3px;padding:0 4px;font-weight:700;">POSTER</span>`
          : ''
        return `<tr style="border-top:1px solid #f1f5f9;">
          <td style="padding:6px 10px;color:#9ca3af;width:28px;">${i + 1}</td>
          <td style="padding:6px 10px;font-weight:600;color:#111827;">${esc(e.presenter_name || '—')}${sub}</td>
          <td style="padding:6px 10px;width:76px;color:#4b5563;">${esc(e.session || '—')}</td>
          <td style="padding:6px 10px;color:#374151;">${esc(e.title || e.activity || '')}${poster}</td>
        </tr>`
      }).join('')

      return `<div style="font-family:Arial,Helvetica,sans-serif;color:#1f2937;background:#ffffff;padding:24px 30px;">
        <table style="width:100%;border-collapse:collapse;">
          <tr>
            <td style="width:64px;"><img src="${ecsaCrest}" alt="ECSA" style="width:60px;height:60px;border-radius:50%;border:2px solid rgb(254,80,103);object-fit:contain;padding:3px;background:#ffffff;box-sizing:border-box;"></td>
            <td style="width:64px;"><div style="width:60px;height:60px;border-radius:50%;background:rgb(220,50,75);overflow:hidden;display:flex;align-items:center;justify-content:center;"><img src="${ecsaconmMark}" alt="ECSACONM" style="width:52px;height:52px;object-fit:contain;"></div></td>
            <td style="padding-left:10px;vertical-align:middle;">
              <div style="font-size:20px;font-weight:700;color:#111827;">ECSACONM Scientific Conference</div>
              <div style="font-size:12px;color:#6b7280;margin-top:2px;">Presenters by Room — Room List</div>
            </td>
          </tr>
        </table>
        <div style="height:3px;background:linear-gradient(90deg,rgb(254,80,103),rgb(180,30,55));margin:12px 0 16px;"></div>

        <div style="border:1px solid #e5e7eb;border-radius:8px;overflow:hidden;">
          <div style="background:rgb(0,150,180);color:#ffffff;padding:8px 14px;font-size:14px;font-weight:700;">${esc(room.room)} <span style="font-weight:400;font-size:12px;">· ${esc(room.day)}</span></div>
          <div style="padding:8px 14px;">
            <div style="font-size:11px;color:#6b7280;padding-bottom:6px;">${room.entries.length} presentation${room.entries.length !== 1 ? 's' : ''} · ${room.with_slide} with slides</div>
            <table style="width:100%;border-collapse:collapse;font-size:12px;">
              <thead>
                <tr style="background:#f9fafb;color:#374151;">
                  <th style="text-align:left;padding:6px 10px;width:28px;font-size:10px;text-transform:uppercase;letter-spacing:0.04em;">#</th>
                  <th style="text-align:left;padding:6px 10px;font-size:10px;text-transform:uppercase;letter-spacing:0.04em;">Presenter</th>
                  <th style="text-align:left;padding:6px 10px;width:76px;font-size:10px;text-transform:uppercase;letter-spacing:0.04em;">Session</th>
                  <th style="text-align:left;padding:6px 10px;font-size:10px;text-transform:uppercase;letter-spacing:0.04em;">Title</th>
                </tr>
              </thead>
              <tbody>${rows}</tbody>
            </table>
          </div>
        </div>

        <div style="margin-top:16px;text-align:center;font-size:10px;color:#9ca3af;">www.ecsaconm.org · info@ecsaconm.org</div>
      </div>`
    },
    async exportRoomPDF(room) {
      if (!room.entries.length) {
        this.flash('Nothing to export for this room.', true)
        return
      }
      this.pdfBusy = room.day + room.room
      try {
        this.flash('Preparing PDF…', false)
        // html2pdf.js 0.14's jsPDF v4 `context2d` renderer emits an empty
        // page, so we build the PDF directly: html2canvas -> jsPDF.addImage.
        const hcMod = await import('html2canvas')
        const html2canvas = hcMod.default || hcMod
        const jsMod = await import('jspdf')
        const JsPDF = jsMod.jsPDF || (jsMod.default && jsMod.default.jsPDF) || jsMod.default
        const node = this.$refs.pdfNode
        if (!node) throw new Error('print node missing')
        node.innerHTML = this.buildRoomPdfHtml(room)

        const cleanRoom = room.room.replace(/[^A-Za-z0-9 _-]+/g, '').trim().slice(0, 40) || 'room'
        const canvas = await html2canvas(node, {
          scale: 2,
          useCORS: true,
          backgroundColor: '#ffffff',
          logging: false,
        })
        const pdf = new JsPDF({ unit: 'mm', format: 'a4', orientation: 'portrait' })
        const pageW = pdf.internal.pageSize.getWidth()
        const pageH = pdf.internal.pageSize.getHeight()
        const margin = 10
        const imgW = pageW - margin * 2
        const mmPerPx = imgW / canvas.width
        const imgH = canvas.height * mmPerPx
        const fitH = pageH - margin * 2
        if (imgH <= fitH) {
          pdf.addImage(canvas.toDataURL('image/jpeg', 0.95), 'JPEG', margin, margin, imgW, imgH, undefined, 'FAST')
        } else {
          const pxPerPage = Math.floor(fitH / mmPerPx)
          let srcY = 0
          let parts = 0
          while (srcY < canvas.height) {
            const srcH = Math.min(pxPerPage, canvas.height - srcY)
            const slice = document.createElement('canvas')
            slice.width = canvas.width
            slice.height = srcH
            const sctx = slice.getContext('2d')
            sctx.fillStyle = '#ffffff'
            sctx.fillRect(0, 0, slice.width, slice.height)
            sctx.drawImage(canvas, 0, srcY, canvas.width, srcH, 0, 0, canvas.width, srcH)
            if (parts > 0) pdf.addPage()
            pdf.addImage(slice.toDataURL('image/jpeg', 0.95), 'JPEG', margin, margin, imgW, srcH * mmPerPx, undefined, 'FAST')
            srcY += srcH
            parts++
          }
        }
        pdf.save(`Presenters_${cleanRoom}_${room.day}.pdf`)
        node.innerHTML = ''
        this.flash('PDF exported.', false)
      } catch (e) {
        console.error('Export room PDF failed:', e)
        this.flash('Failed to generate PDF.', true)
      } finally {
        this.pdfBusy = null
      }
    },

    triggerUpload() {
      this.$refs.slideInput.value = ''
      this.$refs.slideInput.click()
    },
    async onSlideSelected(e) {
      const file = e.target.files && e.target.files[0]
      if (!file || !this.manageTarget) return
      this.manageBusy = true
      this.manageErr = ''
      try {
        const form = new FormData()
        form.append('file', file)
        const res = await axios.post(`${this.apiUrl}/programme/${this.manageTarget.id}/upload-presentation`, form, {
          headers: {
            Authorization: `Bearer ${this.accessToken}`,
            'Content-Type': 'multipart/form-data',
          },
        })
        this.manageTarget.presentation_file = res.data.presentation_file
        this.manageTarget.presentation_uploaded_at = new Date().toISOString()
        this.updateAllEntries(this.manageTarget)
        this.flash('Slides uploaded.')
      } catch (err) {
        this.manageErr = err.response?.data?.detail || 'Upload failed.'
      } finally {
        this.manageBusy = false
        if (this.$refs.slideInput) this.$refs.slideInput.value = ''
      }
    },

    // ── add presenter (manual entry) ──────────────────────────
    openAdd() {
      this.addForm = {
        presenter_name: '',
        title: '',
        category: this.entryCategory,
        day: DAY_ORDER.includes(this.activeDay) ? this.activeDay : 'Day 1',
        room: '',
        session: '',
      }
      this.addFile = null
      this.addErr = ''
      this.addOpen = true
    },
    closeAdd() {
      this.addOpen = false
      this.addFile = null
      this.addErr = ''
    },
    triggerAddUpload() {
      this.$refs.addSlideInput.value = ''
      this.$refs.addSlideInput.click()
    },
    async onAddSlideSelected(e) {
      const file = e.target.files && e.target.files[0]
      this.addErr = ''
      if (!file) return
      const ext = (file.name.split('.').pop() || '').toLowerCase()
      if (!['pdf', 'pptx', 'jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp'].includes(ext)) {
        this.addErr = 'Presentation must be a PDF, PPTX or image (jpg, png, gif, bmp, webp).'
        if (this.$refs.addSlideInput) this.$refs.addSlideInput.value = ''
        return
      }
      if (file.size > 100 * 1024 * 1024) {
        this.addErr = 'File must be under 100 MB.'
        if (this.$refs.addSlideInput) this.$refs.addSlideInput.value = ''
        return
      }
      this.addFile = file
    },
    removeAddFile() {
      this.addFile = null
      if (this.$refs.addSlideInput) this.$refs.addSlideInput.value = ''
    },
    async saveAdd() {
      const name = this.addForm.presenter_name.trim()
      if (!name) {
        this.addErr = 'Presenter name is required.'
        return
      }
      this.addBusy = true
      this.addErr = ''
      try {
        const res = await axios.post(`${this.apiUrl}/programme`, {
          presenter_name: name,
          title: this.addForm.title.trim() || null,
          category: this.addForm.category,
          day: this.addForm.day,
          room: this.addForm.room.trim() || null,
          session: this.addForm.session.trim() || null,
        }, {
          params: { event_id: 1, day: this.addForm.day, category: this.addForm.category },
          headers: { Authorization: `Bearer ${this.accessToken}` },
        })
        const entry = res.data

        if (this.addFile) {
          const form = new FormData()
          form.append('file', this.addFile)
          await axios.post(`${this.apiUrl}/programme/${entry.id}/upload-presentation`, form, {
            headers: {
              Authorization: `Bearer ${this.accessToken}`,
              'Content-Type': 'multipart/form-data',
            },
          })
        }

        this.flash(`Added ${name}${this.addFile ? ' with slides.' : '.'}`, false)
        this.addOpen = false
        this.addFile = null
        await this.loadRooms()
      } catch (e) {
        this.addErr = e.response?.data?.detail || 'Failed to add presenter.'
      } finally {
        this.addBusy = false
      }
    },

    // ── manage entry ──────────────────────────────────────────
    openManage(entry) {
      this.manageTarget = entry
      this.manageForm = {
        presenter_name: entry.presenter_name || '',
        is_substitution: !!entry.is_substitution,
        original_presenter: entry.original_presenter || '',
        video_url: entry.video_url || '',
      }
      this.manageErr = ''
      this.manageOpen = true
    },
    closeManage() {
      this.manageOpen = false
      this.manageTarget = null
    },
    async saveManage() {
      if (!this.manageForm.presenter_name.trim()) {
        this.manageErr = 'Presenter name is required.'
        return
      }
      this.manageBusy = true
      this.manageErr = ''
      try {
        const res = await axios.put(`${this.apiUrl}/programme/${this.manageTarget.id}`, {
          presenter_name: this.manageForm.presenter_name,
          is_substitution: !!this.manageForm.is_substitution,
          original_presenter: this.manageForm.is_substitution ? (this.manageForm.original_presenter || null) : null,
          video_url: this.manageForm.video_url || '',
        }, {
          headers: { Authorization: `Bearer ${this.accessToken}` },
        })
        const updated = res.data
        this.updateAllEntries(updated)
        this.manageTarget = updated
        this.flash(updated.is_substitution ? 'Substitution saved.' : 'Presenter updated.')
        this.manageOpen = false
      } catch (e) {
        this.manageErr = e.response?.data?.detail || 'Save failed.'
      } finally {
        this.manageBusy = false
      }
    },
    async removeSlides() {
      if (!confirm('Remove the uploaded slides for this presentation?')) return
      this.manageBusy = true
      this.manageErr = ''
      try {
        await axios.delete(`${this.apiUrl}/programme/${this.manageTarget.id}/presentation`, {
          headers: { Authorization: `Bearer ${this.accessToken}` },
        })
        this.manageTarget.presentation_file = null
        this.manageTarget.presentation_uploaded_at = null
        this.updateAllEntries(this.manageTarget)
        this.flash('Slides removed.')
      } catch (e) {
        this.manageErr = e.response?.data?.detail || 'Remove failed.'
      } finally {
        this.manageBusy = false
      }
    },

    updateAllEntries(updated) {
      const patch = (list) => {
        const idx = list.findIndex(x => x.id === updated.id)
        if (idx >= 0) list.splice(idx, 1, { ...list[idx], ...updated })
      }
      for (const d of this.roomsData) patch(d.entries)
    },

    dayColor(day) {
      return { 'Day 1': '#005988', 'Day 2': '#0a7ea4', 'Day 3': '#0d5c8a', 'Day 1-3': '#b45309', Unassigned: '#6b7280' }[day] || '#6b7280'
    },
    // Maps a "Day N" label to the event's actual calendar date
    // (event_start_date + N-1 days) so past days can be filtered/hidden.
    dayDate(day) {
      const m = /^Day (\d+)$/.exec(day)
      if (!m || !this.eventStartDate) return null
      const d = new Date(this.eventStartDate + 'T00:00:00')
      d.setDate(d.getDate() + (parseInt(m[1], 10) - 1))
      return d
    },
    isDayPast(day) {
      const today = new Date()
      today.setHours(0, 0, 0, 0)
      if (day === 'Day 1-3') {
        // Spans the whole event — only "past" once the event itself ends.
        return this.eventEndDate ? new Date(this.eventEndDate + 'T00:00:00') < today : false
      }
      const d = this.dayDate(day)
      // Unassigned, or no event date to compare against — never auto-hide.
      return d ? d < today : false
    },

    // ── match presenters to submitted abstracts ────────────────────────
    async openMatch() {
      this.matchOpen = true
      this.matchReport = null
      this.matchApplyResult = null
      this.matchErr = ''
      this.matchLoading = true
      try {
        const res = await axios.get(`${this.apiUrl}/programme/match-abstracts`, {
          params: { event_id: 1, category: this.entryCategory },
          headers: { Authorization: `Bearer ${this.accessToken}` },
        })
        this.matchReport = res.data
        // Default every proposed match to selected — reviewing means
        // unticking the ones you're not sure of, not building the list
        // up from nothing.
        this.matchSelected = {}
        for (const m of this.matchReport.matches) this.matchSelected[m.entry_id] = true
      } catch (e) {
        this.matchErr = e.response?.data?.detail || 'Failed to compute matches.'
      } finally {
        this.matchLoading = false
      }
    },
    setAllMatchSelected(value) {
      for (const id of Object.keys(this.matchSelected)) this.matchSelected[id] = value
    },
    previewAbstract(m) {
      const fileUrl = `${this.apiUrl}/abstracts/${m.abstract_id}/preview-presentation`
      const ext = (m.abstract_presentation_ext || '').replace(/^\./, '').toLowerCase()
      const src = ['pdf', 'jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp'].includes(ext)
        ? fileUrl
        : `https://view.officeapps.live.com/op/embed.aspx?src=${encodeURIComponent(fileUrl)}`
      this.preview = {
        open: true,
        name: `${m.corrected_name} — ${m.abstract_title || ''}`,
        src,
        entry: null,
      }
    },
    async applyMatch() {
      const entryIds = Object.keys(this.matchSelected)
        .filter(id => this.matchSelected[id])
        .map(Number)
      if (!entryIds.length) return
      this.matchApplying = true
      this.matchErr = ''
      try {
        const res = await axios.post(`${this.apiUrl}/programme/match-abstracts/apply`, { entry_ids: entryIds }, {
          params: { event_id: 1, category: this.entryCategory },
          headers: { Authorization: `Bearer ${this.accessToken}` },
        })
        this.matchApplyResult = res.data
        await this.loadRooms()
        this.flash(`Confirmed: ${res.data.renamed} name(s) corrected, ${res.data.linked} newly linked.`)
        // Drop what was just applied from the list rather than a full
        // re-fetch — the rest of the review (ticks, scroll position) stays put.
        const appliedIds = new Set(entryIds)
        this.matchReport.matches = this.matchReport.matches.filter(m => !appliedIds.has(m.entry_id))
        for (const id of entryIds) delete this.matchSelected[id]
      } catch (e) {
        this.matchErr = e.response?.data?.detail || 'Failed to apply matches.'
      } finally {
        this.matchApplying = false
      }
    },
    async linkAbstract(entryId) {
      const abstractId = this.linkChoice[entryId]
      if (!abstractId) return
      this.linkBusy = true
      this.matchErr = ''
      try {
        await axios.put(`${this.apiUrl}/programme/${entryId}/link-abstract`, { abstract_id: Number(abstractId) }, {
          headers: { Authorization: `Bearer ${this.accessToken}` },
        })
        delete this.linkChoice[entryId]
        this.flash('Linked.')
        await this.openMatch()
        await this.loadRooms()
      } catch (e) {
        this.matchErr = e.response?.data?.detail || 'Failed to link.'
      } finally {
        this.linkBusy = false
      }
    },

    flash(msg, err = false) {
      this.flashMsg = msg
      this.flashErr = err
      setTimeout(() => { this.flashMsg = ''; this.flashErr = false }, 4000)
    },

    // ── assign presenters to rooms ───────────────────────────────────
    async openAssignPresenters() {
      this.assignOpen = true
      this.assignLoading = true
      this.assignErr = ''
      this.assignDone = null
      this.assignCategory = 'all'
      this.assignSearch = ''
      // Default to the first day that actually has room slots.
      this.assignForm.day = this.assignDays[0] || 'Day 2'
      this.assignForm.room = ''
      try {
        const res = await axios.get(`${this.apiUrl}/programme/presenters-with-slides`, {
          params: { event_id: 1 },
          headers: { Authorization: `Bearer ${this.accessToken}` },
        })
        // Already-assigned presenters are pointless clutter here — this
        // modal is for assigning people who still need a room, not for
        // moving/reassigning someone already placed (do that from the room
        // card's pencil icon instead).
        this.assignRows = (res.data.data || []).filter(r => !r.assigned)
        this.assignSelected = {}
        for (const r of this.assignRows) {
          this.assignSelected[r.abstract_id] = true
        }
      } catch (e) {
        this.assignErr = e.response?.data?.detail || 'Failed to load presenters.'
      } finally {
        this.assignLoading = false
      }
    },
    selectAssignDay(day) {
      this.assignForm.day = day
      this.assignForm.room = ''
    },
    selectAssignRoom(room) {
      this.assignForm.room = room === this.assignForm.room ? '' : room
    },
    setAssignAll(value) {
      for (const r of this.assignFilteredRows) this.assignSelected[r.abstract_id] = value
    },
    previewAssignAbstract(r) {
      const fileUrl = `${this.apiUrl}/abstracts/${r.abstract_id}/preview-presentation`
      const ext = (r.presentation_ext || '').replace(/^\./, '').toLowerCase()
      const src = ['pdf', 'jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp'].includes(ext)
        ? fileUrl
        : `https://view.officeapps.live.com/op/embed.aspx?src=${encodeURIComponent(fileUrl)}`
      this.preview = {
        open: true,
        name: `${r.presenter} — ${r.title || ''}`,
        src,
        entry: null,
      }
    },
    async submitAssign() {
      const ids = this.assignFilteredRows
        .filter(r => this.assignSelected[r.abstract_id])
        .map(r => r.abstract_id)
      if (!ids.length) return
      if (!this.assignForm.day) { this.assignErr = 'Pick a day first.'; return }
      if (!this.assignForm.room.trim()) { this.assignErr = 'Pick or type a room first.'; return }
      const category = this.assignCategory === 'all' ? null : this.assignCategory
      this.assignBusy = true
      this.assignErr = ''
      this.assignDone = null
      try {
        const res = await axios.post(`${this.apiUrl}/programme/assign-presenters`, {
          abstract_ids: ids,
          room: this.assignForm.room.trim(),
          day: this.assignForm.day,
          category,
        }, {
          params: { event_id: 1 },
          headers: { Authorization: `Bearer ${this.accessToken}` },
        })
        this.assignDone = res.data.detail
        await this.loadRooms()
        await this.openAssignPresenters()
        this.flash(res.data.detail)
      } catch (e) {
        this.assignErr = e.response?.data?.detail || 'Assignment failed.'
      } finally {
        this.assignBusy = false
      }
    },

    // ── bulk file matcher ──────────────────────────────────────
    async openBulkUpload() {
      this.bulkOpen = true
      this.bulkErr = ''
      this.bulkRows = []
      this.bulkProgress = { done: 0, total: 0 }
      if (this.bulkTargets.length) return
      this.bulkTargetsLoading = true
      this.bulkTargetsErr = ''
      try {
        const res = await axios.get(`${this.apiUrl}/programme/match-targets`, {
          params: { event_id: 1 },
          headers: { Authorization: `Bearer ${this.accessToken}` },
        })
        this.bulkTargets = res.data.data || []
      } catch (e) {
        this.bulkTargetsErr = e.response?.data?.detail || 'Failed to load the programme for matching.'
      } finally {
        this.bulkTargetsLoading = false
      }
    },
    closeBulkUpload() {
      if (this.bulkBusy) return
      this.bulkOpen = false
    },
    onBulkFilesChosen(e) {
      const files = Array.from(e.target.files || [])
      if (!files.length) return
      const rows = files.map(file => {
        const { entry, confidence, reason } = bulkBestMatch(file.name, this.bulkTargets)
        const tooLarge = file.size > BULK_MAX_UPLOAD_BYTES
        return {
          file,
          name: file.name,
          sizeLabel: this.formatFileSize(file.size),
          entryId: entry ? entry.id : null,
          entry: entry || null,
          pickText: entry ? bulkEntryLabel(entry) : '',
          confidence,
          reason,
          tooLarge,
          // Only auto-include files we're at least reasonably sure about —
          // "low"/"none" still show up (so nothing silently gets skipped)
          // but need the admin to actively confirm a target first. A file
          // over the Cloudflare cap can never succeed here regardless of
          // match confidence, so it's never auto-included.
          include: !tooLarge && (confidence === 'high' || confidence === 'medium'),
          status: 'pending', // pending | uploading | done | error
          error: '',
          progress: 0, // 0-100, this file's own upload percentage
        }
      })
      this.bulkRows = [...this.bulkRows, ...rows]
      if (this.$refs.bulkFileInput) this.$refs.bulkFileInput.value = ''
    },
    removeBulkRow(row) {
      this.bulkRows = this.bulkRows.filter(r => r !== row)
    },
    resolveBulkPick(row) {
      const m = (row.pickText || '').match(/^#(\d+)/)
      if (!m) {
        row.entryId = null
        row.entry = null
        return
      }
      const id = Number(m[1])
      const entry = this.bulkTargets.find(t => t.id === id) || null
      row.entryId = entry ? entry.id : null
      row.entry = entry
      if (entry) row.include = true
    },
    bulkConfidenceLabel(c) {
      return { high: 'Code match', medium: 'Name match', low: 'Weak match', none: 'No match' }[c] || ''
    },
    bulkConfidenceClass(c) {
      return {
        high: 'bg-green-100 text-green-700',
        medium: 'bg-blue-100 text-blue-700',
        low: 'bg-amber-100 text-amber-700',
        none: 'bg-gray-100 text-gray-500',
      }[c] || 'bg-gray-100 text-gray-500'
    },
    formatFileSize(bytes) {
      if (!bytes && bytes !== 0) return ''
      const mb = bytes / (1024 * 1024)
      return mb >= 1 ? `${mb.toFixed(1)} MB` : `${Math.max(1, Math.round(bytes / 1024))} KB`
    },
    async runBulkUpload() {
      const rows = this.bulkRows.filter(r => r.include && r.entryId && !r.tooLarge && r.status !== 'done')
      if (!rows.length) return
      this.bulkBusy = true
      this.bulkErr = ''
      // Byte-based, not just a file count — with a few hundred-MB videos in
      // the mix, "3 of 75 files" barely moves while the big one is mid-flight,
      // so the overall bar tracks total bytes sent across the whole batch.
      const totalBytes = rows.reduce((s, r) => s + (r.file.size || 0), 0)
      let bytesDoneBeforeCurrent = 0
      this.bulkProgress = { done: 0, total: rows.length, totalBytes, sentBytes: 0, percent: 0 }
      // Sequential, not parallel — some of these files run into the
      // hundreds of MB (embedded video), so uploading one at a time avoids
      // saturating the admin's own upload bandwidth across many at once and
      // keeps per-file progress/errors easy to attribute.
      for (const row of rows) {
        row.status = 'uploading'
        row.error = ''
        row.progress = 0
        try {
          const form = new FormData()
          form.append('file', row.file)
          const res = await axios.post(`${this.apiUrl}/programme/${row.entryId}/upload-presentation`, form, {
            headers: {
              Authorization: `Bearer ${this.accessToken}`,
              'Content-Type': 'multipart/form-data',
            },
            // Safety net only — every row here is already under the 95MB
            // Cloudflare ceiling, so this should never legitimately be hit;
            // it just stops a genuinely dead connection from freezing the
            // rest of the batch indefinitely.
            timeout: 10 * 60 * 1000,
            onUploadProgress: (evt) => {
              const rowTotal = evt.total || row.file.size || 1
              row.progress = Math.min(100, Math.round((evt.loaded / rowTotal) * 100))
              this.bulkProgress.sentBytes = bytesDoneBeforeCurrent + evt.loaded
              this.bulkProgress.percent = totalBytes
                ? Math.min(100, Math.round((this.bulkProgress.sentBytes / totalBytes) * 100))
                : 0
            },
          })
          row.status = 'done'
          row.progress = 100
          const target = this.bulkTargets.find(t => t.id === row.entryId)
          if (target) {
            target.has_presentation = true
            target.presentation_uploaded_at = new Date().toISOString()
          }
          this.updateAllEntries({ id: row.entryId, presentation_file: res.data.presentation_file, presentation_uploaded_at: new Date().toISOString() })
        } catch (e) {
          row.status = 'error'
          if (e.code === 'ECONNABORTED') {
            row.error = 'Timed out — connection stalled. Check your internet and retry.'
          } else if (e.response?.status === 413) {
            row.error = 'Rejected as too large by the server/CDN.'
          } else {
            row.error = e.response?.data?.detail || 'Upload failed.'
          }
        } finally {
          this.bulkProgress.done++
          bytesDoneBeforeCurrent += row.file.size || 0
          this.bulkProgress.sentBytes = bytesDoneBeforeCurrent
          this.bulkProgress.percent = totalBytes ? Math.min(100, Math.round((bytesDoneBeforeCurrent / totalBytes) * 100)) : 0
        }
      }
      this.bulkBusy = false
      const okCount = rows.filter(r => r.status === 'done').length
      const failCount = rows.filter(r => r.status === 'error').length
      this.flash(
        `Uploaded ${okCount} file${okCount !== 1 ? 's' : ''}.` + (failCount ? ` ${failCount} failed — see the list below.` : ''),
        failCount > 0 && okCount === 0,
      )
      await this.loadRooms()
    },
  },
}
</script>

<style scoped>
.chip {
  @apply px-3 py-1.5 rounded-full text-xs font-semibold border transition;
}
.chip--idle {
  @apply text-gray-600 border-gray-200 bg-white hover:border-gray-300;
}
.chip--active {
  @apply text-white;
  background-color: rgb(254, 80, 103);
  border-color: rgb(254, 80, 103);
}
.badge {
  @apply inline-flex items-center px-2 py-0.5 rounded text-[11px] font-semibold;
}
.badge-sub { @apply badge bg-purple-100 text-purple-700; }
.badge-warn { @apply badge bg-orange-100 text-orange-700; }
.action-btn {
  @apply flex items-center justify-center w-8 h-8 rounded-lg border border-gray-200 bg-white text-gray-500 hover:bg-gray-50 transition-colors flex-shrink-0;
}
.field-input {
  @apply w-full rounded-lg border border-gray-200 bg-white px-3 py-2 text-sm text-on-surface focus:outline-none focus:ring-2 focus:ring-cp-secondary;
}
</style>