<template>
  <div class="flex flex-col space-y-4 flex-1">
    <HeaderView :headerTitle="'Presentations by Room'" />

    <div v-if="flashMsg" class="px-3 py-2 rounded-md text-sm"
      :class="flashErr ? 'bg-red-50 text-red-600' : 'bg-green-50 text-green-600'">
      {{ flashMsg }}
    </div>

    <!-- PIN gate -->
    <div v-if="!unlocked" class="max-w-md mx-auto w-full mt-6">
      <div class="rounded-xl border border-surface-container-high bg-surface-container-lowest p-6">
        <div class="flex items-center gap-2 mb-1">
          <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.75">
            <rect x="3" y="11" width="18" height="11" rx="2"/><path d="M7 11V7a5 5 0 0110 0v4"/>
          </svg>
          <div class="font-bold">Rooms access is PIN-protected</div>
        </div>
        <p class="text-xs text-gray-500 mb-4">
          Enter the admin Rooms PIN to view the timetable by room, preview slides and download presentations.
        </p>
        <div v-if="pinConfigured === false" class="mb-4 text-xs text-amber-700 bg-amber-50 border border-amber-200 rounded-lg p-3">
          No Rooms PIN is configured yet. Set one below — everyone viewing this page will need it.
        </div>
        <input v-model.trim="pinInput" type="password" class="field-input text-center tracking-[0.5em] py-3"
          placeholder="••••••" maxlength="20" @keyup.enter="submitPin" />
        <div v-if="pinError" class="mt-2 text-sm text-red-600">{{ pinError }}</div>
        <div class="mt-4 flex flex-col gap-2">
          <button @click="submitPin" :disabled="pinBusy" class="px-4 py-2.5 text-sm font-semibold text-white rounded-lg transition"
            style="background-color: rgb(254,80,103);">
            {{ pinBusy ? 'Checking…' : 'Unlock rooms' }}
          </button>
          <button v-if="isAdmin" @click="openPinSetup" class="px-4 py-2 text-sm font-medium text-gray-600 hover:bg-gray-50 rounded-lg border border-gray-200">
            {{ pinConfigured === false ? 'Set PIN' : 'Change PIN' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Rooms view -->
    <template v-else>
      <!-- category toggle: abstracts (oral) vs posters -->
      <div class="flex items-center gap-2">
        <button v-for="c in categoryOptions" :key="c.key"
          @click="entryCategory = c.key"
          class="chip" :class="entryCategory === c.key ? 'chip--active' : 'chip--idle'">
          {{ c.label }}
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
        <button v-if="isAdmin" @click="openMatch" :disabled="matchLoading"
          class="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-semibold border"
          style="border-color: rgb(0,150,180); color: rgb(0,150,180);">
          <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.75">
            <path stroke-linecap="round" stroke-linejoin="round" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          {{ matchLoading ? 'Matching…' : `Match ${entryCategory === 'poster' ? 'Posters' : 'Abstracts'}` }}
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
                  <button v-if="room.with_slide" @click="downloadRoomZip(room)"
                    :disabled="zipBusy"
                    class="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-[11px] font-semibold bg-white text-cp-secondary hover:opacity-90">
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
                      <span v-if="e.status === 'not_registered'" class="badge badge-warn" title="Name not matched to a registered person">⚠</span>
                    </div>
                    <div class="text-xs text-gray-500 mt-0.5 flex flex-wrap items-center gap-x-2 gap-y-0.5">
                      <span v-if="e.code" class="font-mono">{{ e.code }}</span>
                      <span v-if="e.session">Session {{ e.session }}</span>
                      <span v-if="e.category === 'poster'" class="uppercase tracking-wide text-amber-600">Poster</span>
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
                    <span v-if="!e.has_presentation" class="text-[10px] text-gray-400 italic">no slides yet</span>
                    <span v-else-if="e.presentation_source === 'abstract'" class="text-[9px] text-teal-600 font-semibold uppercase tracking-wide">from abstract</span>
                    <button @click="openManage(e)" title="Replace presenter / add slides"
                      class="action-btn hover:border-cp-secondary">
                      <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.75">
                        <path stroke-linecap="round" stroke-linejoin="round" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                      </svg>
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </template>

    <!-- PIN setup modal -->
    <div v-if="pinSetupOpen" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/40" @click.self="pinSetupOpen = false">
      <div class="bg-white rounded-xl shadow-xl w-full max-w-sm p-5">
        <div class="font-bold mb-1">{{ pinConfigured === false ? 'Set Rooms PIN' : 'Change Rooms PIN' }}</div>
        <p class="text-xs text-gray-500 mb-3">Admins viewing the Presentations by Room page will be asked for this PIN before slides and downloads are shown.</p>
        <input v-model.trim="newPin" type="text" class="field-input text-center tracking-[0.5em]" maxlength="20" />
        <div v-if="pinSetupErr" class="mt-2 text-sm text-red-600">{{ pinSetupErr }}</div>
        <div class="mt-4 flex justify-end gap-2">
          <button @click="pinSetupOpen = false" class="px-4 py-2 text-sm font-medium text-gray-600 rounded-lg">Cancel</button>
          <button @click="savePin" :disabled="pinBusy" class="px-4 py-2 text-sm font-semibold text-white rounded-lg"
            style="background-color: rgb(254,80,103);">Save PIN</button>
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
              <div class="font-semibold text-sm">Proposed matches</div>
              <div class="rounded-lg border border-gray-200 divide-y divide-gray-100 max-h-64 overflow-y-auto">
                <div v-for="m in matchReport.matches" :key="m.entry_id" class="px-3 py-2 text-sm">
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
                </div>
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
                  <div class="text-xs text-gray-500 truncate">{{ u.title }}</div>
                </div>
              </div>
            </div>
          </template>
          <div v-if="matchErr" class="px-3 py-2 rounded-md bg-red-50 text-red-600 text-sm">{{ matchErr }}</div>
        </div>
        <div class="px-5 py-4 border-t border-gray-100 flex justify-end gap-2 sticky bottom-0 bg-white">
          <button @click="matchOpen = false" class="px-4 py-2 text-sm font-medium text-gray-600 hover:bg-gray-50 rounded-lg">Close</button>
          <button v-if="matchReport && matchReport.matches.length" @click="applyMatch" :disabled="matchApplying"
            class="px-4 py-2 text-sm font-semibold text-white rounded-lg" style="background-color: rgb(254,80,103);">
            {{ matchApplying ? 'Applying…' : `Apply ${matchReport.matches.length} matches` }}
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
            <button @click="downloadSingle(preview.entry)"
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
  </div>
</template>

<script>
import HeaderView from '@/includes/Header.vue'
import SpinnerComponent from '@/components/Spinner.vue'
import { useAuthStore } from '@/store/authStore'
import { saveAs } from 'file-saver'
import axios from 'axios'

const DAY_ORDER = ['Day 1', 'Day 2', 'Day 3', 'Day 1-3', 'Unassigned']
const PIN_STORAGE_KEY = 'ecsaconm_rooms_pin'

export default {
  name: 'ProgrammeRoomsView',
  components: { HeaderView, SpinnerComponent },

  data() {
    return {
      roomsData: [],
      loading: false,
      unlocked: false,
      pinInput: '',
      pinConfigured: null,   // null = unknown, true/false
      pinError: '',
      pinBusy: false,
      activeRoom: 'All Rooms',
      entryCategory: 'oral',
      categoryOptions: [
        { key: 'oral', label: 'Abstracts' },
        { key: 'poster', label: 'Posters' },
      ],
      apiUrl: import.meta.env.VITE_API_URL,
      flashMsg: '', flashErr: false,
      pinSetupOpen: false, newPin: '', pinSetupErr: '',
      manageOpen: false, manageTarget: null, manageForm: {}, manageBusy: false, manageErr: '',
      preview: { open: false, name: '', src: '', entry: null },
      zipBusy: false,
      matchOpen: false, matchLoading: false, matchReport: null, matchErr: '',
      matchApplying: false, matchApplyResult: null,
      linkChoice: {}, linkBusy: false,
      acceptedExtensions: '.pdf,.pptx,.jpg,.jpeg,.png,.gif,.bmp,.webp',
      _roomPin: '',
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
    roomDays() {
      const grouped = {}
      for (const d of this.categoryRoomsData) {
        if (this.activeRoom !== 'All Rooms' && d.room !== this.activeRoom) continue
        ;(grouped[d.day] = grouped[d.day] || []).push(d)
      }
      return DAY_ORDER.filter(day => grouped[day]).map(day => ({
        day,
        rooms: grouped[day],
        total: grouped[day].reduce((s, r) => s + r.total, 0),
      }))
    },
    slideCountSummary() {
      const total = this.categoryRoomsData.reduce((s, d) => s + d.entries.length, 0)
      const withSlide = this.categoryRoomsData.reduce((s, d) => s + d.entries.filter(e => e.has_presentation).length, 0)
      return `${withSlide} of ${total} presentations have slides`
    },
  },

  watch: {
    // Room chips are category-specific (e.g. "Poster Area" only exists for
    // posters) — a stale pick from the other category would just show
    // nothing, so reset it whenever the category switches.
    entryCategory() {
      this.activeRoom = 'All Rooms'
    },
  },

  mounted() {
    this.checkPin()
  },

  methods: {
    async checkPin() {
      const stored = sessionStorage.getItem(PIN_STORAGE_KEY)
      if (stored) {
        this._roomPin = stored
        this.unlocked = true
        this.loadRooms()
        return
      }
      try {
        const res = await axios.get(`${this.apiUrl}/programme/pin/status`, {
          headers: { Authorization: `Bearer ${this.accessToken}` },
        })
        this.pinConfigured = !!res.data.set
      } catch (e) {
        this.flash('Failed to check PIN status.', true)
      }
    },

    async submitPin() {
      const pin = this.pinInput.trim()
      if (!pin) { this.pinError = 'Enter the rooms PIN.'; return }
      this.pinBusy = true
      this.pinError = ''
      try {
        const res = await axios.post(`${this.apiUrl}/programme/pin/verify`, { pin }, {
          headers: { Authorization: `Bearer ${this.accessToken}` },
        })
        if (res.data.valid) {
          this._roomPin = pin
          sessionStorage.setItem(PIN_STORAGE_KEY, pin)
          this.unlocked = true
          this.pinConfigured = true
          this.loadRooms()
        } else {
          this.pinError = 'Incorrect PIN.'
        }
      } catch (e) {
        this.pinError = e.response?.data?.detail || 'Verification failed.'
      } finally {
        this.pinBusy = false
      }
    },

    openPinSetup() {
      this.newPin = ''
      this.pinSetupErr = ''
      this.pinSetupOpen = true
    },
    async savePin() {
      if (!this.newPin.trim() || this.newPin.trim().length < 4) {
        this.pinSetupErr = 'PIN must be at least 4 characters.'
        return
      }
      this.pinBusy = true
      this.pinSetupErr = ''
      try {
        await axios.put(`${this.apiUrl}/programme/pin`, { pin: this.newPin.trim() }, {
          headers: { Authorization: `Bearer ${this.accessToken}` },
        })
        this.pinConfigured = true
        this.pinSetupOpen = false
        this.flash('Rooms PIN updated.')
      } catch (e) {
        this.pinSetupErr = e.response?.data?.detail || 'Failed to save PIN.'
      } finally {
        this.pinBusy = false
      }
    },

    async loadRooms() {
      this.loading = true
      try {
        const res = await axios.get(`${this.apiUrl}/programme/rooms`, {
          params: { event_id: 1 },
          headers: { Authorization: `Bearer ${this.accessToken}`, 'X-Room-Pin': this._roomPin },
        })
        this.roomsData = res.data.data || []
      } catch (e) {
        if (e.response?.status === 401 || e.response?.status === 403) {
          sessionStorage.removeItem(PIN_STORAGE_KEY)
          this.unlocked = false
          this.flash(e.response?.data?.detail || 'Invalid session PIN.', true)
        } else {
          this.flash('Failed to load rooms.', true)
        }
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
      try {
        const res = await axios.get(`${this.apiUrl}/programme/download-room-zip`, {
          params: { event_id: 1, room: room.room, day: room.day },
          responseType: 'blob',
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
            'X-Room-Pin': this._roomPin,
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

    // ── manage entry ──────────────────────────────────────────
    openManage(entry) {
      this.manageTarget = entry
      this.manageForm = {
        presenter_name: entry.presenter_name || '',
        is_substitution: !!entry.is_substitution,
        original_presenter: entry.original_presenter || '',
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
        }, {
          headers: { Authorization: `Bearer ${this.accessToken}`, 'X-Room-Pin': this._roomPin },
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
          headers: { Authorization: `Bearer ${this.accessToken}`, 'X-Room-Pin': this._roomPin },
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
      } catch (e) {
        this.matchErr = e.response?.data?.detail || 'Failed to compute matches.'
      } finally {
        this.matchLoading = false
      }
    },
    async applyMatch() {
      this.matchApplying = true
      this.matchErr = ''
      try {
        const res = await axios.post(`${this.apiUrl}/programme/match-abstracts/apply`, {}, {
          params: { event_id: 1, category: this.entryCategory },
          headers: { Authorization: `Bearer ${this.accessToken}` },
        })
        this.matchApplyResult = res.data
        await this.loadRooms()
        this.flash(`Applied: ${res.data.renamed} name(s) corrected, ${res.data.linked} newly linked.`)
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