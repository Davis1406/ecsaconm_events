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
        <button v-if="isAdmin" @click="openAssignPresenters" :disabled="assignBusy"
          class="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-semibold border"
          style="border-color: rgb(254,80,103); color: rgb(254,80,103);">
          <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.75">
            <path stroke-linecap="round" stroke-linejoin="round" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
          </svg>
          Assign to Room
        </button>
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
              <span class="text-xs text-gray-400">Day 1 is already assigned, so it's not offered here.</span>
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
                      <span v-if="r.assigned" class="inline-flex items-center gap-1 text-[10px] font-semibold px-1.5 py-0.5 rounded bg-green-100 text-green-700 uppercase tracking-wide">
                        <svg class="w-2.5 h-2.5" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"/></svg>
                        in room
                      </span>
                      <span v-if="r.presentation_ext" class="text-[10px] font-semibold px-1.5 py-0.5 rounded bg-gray-100 text-gray-600 uppercase">{{ r.presentation_ext }}</span>
                      <span class="text-[10px] font-semibold px-1.5 py-0.5 rounded uppercase"
                        :class="r.presentation_type === 'poster' ? 'bg-amber-100 text-amber-700' : 'bg-blue-100 text-blue-700'">
                        {{ r.presentation_type }}
                      </span>
                    </div>
                    <div class="text-xs text-gray-500 truncate mt-0.5">{{ r.title }}</div>
                    <div v-if="r.assigned && r.entries.length" class="text-[10px] text-green-700 mt-0.5">
                      Current: {{ r.entries[0].day }} · {{ r.entries[0].room }}<template v-if="r.entries[0].session"> · {{ r.entries[0].session }}</template>
                    </div>
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
  </div>
</template>

<script>
import HeaderView from '@/includes/Header.vue'
import SpinnerComponent from '@/components/Spinner.vue'
import { useAuthStore } from '@/store/authStore'
import { saveAs } from 'file-saver'
import axios from 'axios'

const DAY_ORDER = ['Day 1', 'Day 2', 'Day 3', 'Day 1-3', 'Unassigned']

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
      ],
      apiUrl: import.meta.env.VITE_API_URL,
      flashMsg: '', flashErr: false,
      manageOpen: false, manageTarget: null, manageForm: {}, manageBusy: false, manageErr: '',
      preview: { open: false, name: '', src: '', entry: null },
      zipBusy: false,
      zipProgress: { active: false, room: '', percent: 0, loadedMB: '0.0', totalMB: null },
      roomDeleting: null,
      matchOpen: false, matchLoading: false, matchReport: null, matchErr: '',
      matchApplying: false, matchApplyResult: null, matchSelected: {},
      linkChoice: {}, linkBusy: false,
      acceptedExtensions: '.pdf,.pptx,.jpg,.jpeg,.png,.gif,.bmp,.webp',
      // assign presenters state
      assignOpen: false, assignLoading: false, assignRows: [], assignCategory: 'all',
      assignSearch: '',
      assignErr: '', assignDone: null, assignBusy: false, assignSelected: {},
      assignForm: { room: '', day: 'Day 2' },
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
      // Day 1 assignments are already done, so it's no longer offered here.
      // Every other single conference day is offered regardless of whether
      // it already has room entries — rooms can be freeform-typed in step 2.
      return DAY_ORDER.filter(day => /^Day \d+$/.test(day) && day !== 'Day 1')
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
        this.assignRows = res.data.data || []
        this.assignSelected = {}
        for (const r of this.assignRows) {
          if (!r.assigned) this.assignSelected[r.abstract_id] = true
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