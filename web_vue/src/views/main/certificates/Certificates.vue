<template>
  <div class="flex flex-col space-y-4 flex-1">
    <HeaderView :headerTitle="'Certificates'" />

    <!-- Event + certificate type -->
    <div class="bg-white border border-gray-100 rounded-xl shadow-sm p-5 space-y-4">
      <div>
        <label class="block text-xs font-bold uppercase tracking-widest text-gray-400 mb-1.5">Select Event</label>
        <select v-model="selectedEventId" @change="loadPeople"
          class="w-full border border-gray-200 rounded-xl px-3 py-2.5 text-sm text-gray-700 focus:outline-none bg-white">
          <option value="">— Choose an event —</option>
          <option v-for="event in events" :key="event.id" :value="event.id">{{ event.event }}</option>
        </select>
      </div>

      <div>
        <label class="block text-xs font-bold uppercase tracking-widest text-gray-400 mb-1.5">Certificate Type</label>
        <div class="flex flex-wrap items-center gap-2">
          <button v-for="(t, key) in types" :key="key" type="button" @click="setType(key)"
            class="px-4 py-2 rounded-xl text-xs font-semibold transition"
            :class="type === key ? 'text-white' : 'bg-gray-50 text-gray-600 hover:bg-gray-100'"
            :style="type === key ? { backgroundColor: 'rgb(254,80,103)' } : {}">
            {{ t.label }} <span class="opacity-80 ml-1">· {{ t.cpd }} CPD</span>
          </button>
          <button type="button" @click="preview"
            class="ml-auto inline-flex items-center gap-1.5 px-4 py-2 rounded-xl text-xs font-semibold text-gray-600 bg-gray-50 hover:bg-gray-100 transition">
            <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
            </svg>
            Preview Template
          </button>
        </div>
        <p class="text-xs text-gray-400 mt-2">{{ sourceHint }}</p>
      </div>
    </div>

    <!-- No event selected -->
    <div v-if="!selectedEventId" class="bg-white rounded-2xl shadow-sm py-20 flex flex-col items-center justify-center text-center px-6">
      <p class="text-gray-500 text-base font-medium mb-1">Select an event to generate certificates</p>
      <p class="text-gray-400 text-sm">Presenters (plenary, oral &amp; poster), ushers/secretariat, and other paid delegates are loaded from the event</p>
    </div>

    <!-- Spinner -->
    <div v-else-if="isLoading" class="flex justify-center py-12">
      <svg class="animate-spin h-8 w-8" style="color: rgb(254,80,103);" fill="none" viewBox="0 0 24 24">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"/>
      </svg>
    </div>

    <template v-else>
      <div class="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden">
        <!-- Toolbar -->
        <div class="px-4 py-3 border-b border-gray-200 flex flex-wrap items-center gap-x-3 gap-y-2">
          <div class="relative">
            <svg class="w-3.5 h-3.5 absolute left-2.5 top-1/2 -translate-y-1/2 text-gray-400 pointer-events-none"
              fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M21 21l-4.35-4.35M17 11a6 6 0 11-12 0 6 6 0 0112 0z"/>
            </svg>
            <input v-model="search" type="text" placeholder="Search name or email"
              class="w-56 pl-8 pr-3 py-1.5 text-[13px] border border-gray-200 rounded-md bg-white text-gray-700
                     placeholder:text-gray-400 focus:outline-none focus:border-brand focus:ring-2 focus:ring-brand/15" />
          </div>

          <label v-if="type === 'attendee'"
            class="inline-flex items-center gap-1.5 text-[12px] text-gray-500 font-medium select-none cursor-pointer">
            <input type="checkbox" v-model="attendedOnly" class="rounded border-gray-300 text-brand focus:ring-brand/30" />
            Scanned as attended
          </label>

          <div class="flex flex-wrap items-center gap-1.5">
            <button type="button" @click="emailOnly = !emailOnly" :aria-pressed="emailOnly"
              class="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md text-[12px] font-medium border transition"
              :class="emailOnly
                ? 'text-white border-transparent'
                : 'text-gray-500 border-gray-200 bg-white hover:border-gray-300 hover:text-gray-700'"
              :style="emailOnly ? { backgroundColor: 'rgb(254,80,103)' } : {}">
              <svg class="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
                <path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7"/>
              </svg>
              Has email
              <span class="tabular-nums opacity-70">{{ withEmailCount }}</span>
            </button>

            <template v-if="type === 'attendee'">
              <button v-for="c in attendeeCategories" :key="c.name" type="button" @click="toggleAttendeeCategory(c.name)"
                :aria-pressed="attendeeCategoryFilter.includes(c.name)"
                class="px-2.5 py-1 rounded-md text-[12px] font-medium border transition capitalize"
                :class="attendeeCategoryFilter.includes(c.name)
                  ? 'text-white border-transparent'
                  : 'text-gray-500 border-gray-200 bg-white hover:border-gray-300 hover:text-gray-700'"
                :style="attendeeCategoryFilter.includes(c.name) ? { backgroundColor: 'rgb(254,80,103)' } : {}">
                {{ c.name }} <span class="tabular-nums opacity-70">{{ c.count }}</span>
              </button>
            </template>

            <template v-if="type === 'presenter'">
              <button v-for="c in presenterCategories" :key="c.name" type="button" @click="toggleCategory(c.name)"
                :aria-pressed="categoryFilter.includes(c.name)"
                class="px-2.5 py-1 rounded-md text-[12px] font-medium border transition capitalize"
                :class="categoryFilter.includes(c.name)
                  ? 'text-white border-transparent'
                  : 'text-gray-500 border-gray-200 bg-white hover:border-gray-300 hover:text-gray-700'"
                :style="categoryFilter.includes(c.name) ? { backgroundColor: 'rgb(254,80,103)' } : {}">
                {{ presenterCategoryLabel(c.name) }}
                <span class="tabular-nums opacity-70">{{ c.count }}</span>
              </button>
            </template>
          </div>

          <div class="ml-auto flex items-baseline gap-1.5 text-[12px] tabular-nums">
            <span class="text-gray-400">{{ filteredPeople.length }} shown</span>
            <span v-if="selectedCount" class="text-gray-900 font-semibold">· {{ selectedCount }} selected</span>
          </div>
        </div>

        <div class="overflow-x-auto max-h-[60vh] overflow-y-auto">
          <table class="w-full min-w-[760px] text-[13px]">
            <thead class="sticky top-0 z-10">
              <tr class="bg-white text-[11px] font-semibold uppercase tracking-[0.07em] text-gray-400 border-b border-gray-200">
                <th class="pl-4 pr-2 py-2.5 text-left w-9">
                  <input type="checkbox" :checked="allShownSelected" @change="toggleAllShown($event.target.checked)"
                    class="rounded border-gray-300 text-brand focus:ring-brand/30" title="Select all shown" />
                </th>
                <th class="px-2 py-2.5 text-left w-10" title="Row number">#</th>
                <th class="px-2 py-2.5 text-left">Name on certificate</th>
                <th class="px-2 py-2.5 text-left">Email</th>
                <th v-if="type !== 'presenter'" class="px-2 py-2.5 text-left whitespace-nowrap">Category</th>
                <th class="px-2 py-2.5 text-left">{{ type === 'presenter' ? 'Presentation' : 'Country' }}</th>
                <th class="pl-2 pr-4 py-2.5 text-right whitespace-nowrap">Action</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-100">
              <tr v-for="(p, idx) in filteredPeople" :key="p.key"
                class="group transition-colors hover:bg-brand/[0.035]"
                :class="selected[p.key] ? 'bg-brand/[0.05] shadow-[inset_2px_0_0_rgb(254,80,103)]' : ''">
                <td class="pl-4 pr-2 py-2">
                  <input type="checkbox" :checked="!!selected[p.key]" @change="toggle(p.key, $event.target.checked)"
                    class="rounded border-gray-300 text-brand focus:ring-brand/30" />
                </td>
                <td class="px-2 py-2 text-[11.5px] text-gray-300 tabular-nums">{{ idx + 1 }}</td>
                <td class="px-2 py-2 font-medium text-gray-900 whitespace-nowrap">{{ p.name }}</td>
                <td class="px-2 py-2">
                  <a v-if="p.email" :href="`mailto:${p.email}`"
                    class="text-[12.5px] text-gray-500 hover:text-brand transition-colors break-all">
                    {{ p.email }}
                  </a>
                  <span v-else class="text-[12.5px] text-gray-300">—</span>
                </td>
                <td v-if="type !== 'presenter'" class="px-2 py-2 whitespace-nowrap">
                  <span class="inline-flex items-center rounded-full border border-gray-200 bg-gray-50 px-2 py-0.5 text-[11px] font-medium text-gray-600">
                    {{ p.category }}
                  </span>
                </td>
                <td class="px-2 py-2 text-[12.5px] text-gray-500">
                  <!-- Falls back to the session/category text when a presenter has
                       no presentation title (e.g. abstract-only, no programme slot). -->
                  <span v-if="p.detail || p.category">{{ p.detail || p.category }}</span>
                  <span v-else class="text-gray-300">—</span>
                </td>
                <td class="pl-2 pr-4 py-2 text-right whitespace-nowrap">
                  <button v-if="p.email" type="button" @click="openEmailModal([p])"
                    :disabled="!!emailModal"
                    class="inline-flex items-center gap-1.5 rounded-md border px-2.5 py-1 text-[12px] font-semibold transition
                           disabled:opacity-40 disabled:cursor-not-allowed"
                    :class="rowMsg && rowMsg.key === p.key
                      ? (rowMsg.ok
                          ? 'border-green-200 bg-green-50 text-green-700'
                          : 'border-red-200 bg-red-50 text-red-600')
                      : 'border-gray-200 bg-white text-gray-600 hover:border-brand/50 hover:text-brand hover:bg-brand/5'">
                    <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.8">
                      <path stroke-linecap="round" stroke-linejoin="round" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"/>
                    </svg>
                    {{ rowMsg && rowMsg.key === p.key ? rowMsg.text : 'Preview & Send' }}
                  </button>
                  <span v-else class="text-[12px] text-gray-300 italic">Not emailable</span>
                </td>
              </tr>
            </tbody>
          </table>
          <div v-if="filteredPeople.length === 0" class="py-16 text-center">
            <p class="text-gray-400 text-sm">No one matches the current filters</p>
            <p class="text-gray-300 text-xs mt-1">Clear the filters above, or type names under "Additional names" below</p>
          </div>
        </div>
      </div>

      <!-- Extra names + generate -->
      <div class="bg-white rounded-2xl shadow-sm p-5 space-y-3">
        <div>
          <label class="block text-xs font-bold uppercase tracking-widest text-gray-400 mb-1.5">Additional names</label>
          <textarea v-model="extraNames" rows="4"
            placeholder="Anyone not in the list above — one full name per line, exactly as it should appear"
            class="w-full border border-gray-200 rounded-xl px-3 py-2 text-sm focus:outline-none"></textarea>
        </div>
        <div v-if="emailSuccess" class="p-3 rounded-xl text-sm text-green-700 bg-green-50 border border-green-200">{{ emailSuccess }}</div>

        <div class="flex flex-wrap items-center gap-3">
          <p class="text-xs text-gray-400 flex-1">
            <strong>Generate</strong> opens a print tab — choose <strong>Save as PDF</strong> and turn on
            <strong>Background graphics</strong> for one PDF with a page per person.
            <strong>Email</strong> opens a preview you can edit before sending — each selected person gets their own
            certificate as a PDF at their registration email, followed by the event's public Links (Links tab);
            people typed under "Additional names" have no email on file and are skipped. ALL-CAPS / lowercase names
            are tidied to Title Case.
          </p>
          <button type="button" @click="openEmailModal(emailableSelected)" :disabled="!emailableSelected.length || !!emailModal"
            class="inline-flex items-center gap-1.5 px-5 py-2.5 rounded-xl text-sm font-semibold border-2 transition disabled:opacity-40"
            style="border-color: rgb(254,80,103); color: rgb(254,80,103);">
            <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"/>
            </svg>
            Email {{ emailableSelected.length }} Certificate{{ emailableSelected.length === 1 ? '' : 's' }}
          </button>
          <button type="button" @click="generate" :disabled="!finalNames.length"
            class="inline-flex items-center gap-1.5 px-5 py-2.5 rounded-xl text-sm font-semibold text-white transition hover:opacity-90 disabled:opacity-40"
            style="background-color: rgb(254,80,103);">
            <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M9 12l2 2 4-4M7.835 4.697a3.42 3.42 0 001.946-.806 3.42 3.42 0 014.438 0 3.42 3.42 0 001.946.806 3.42 3.42 0 013.138 3.138 3.42 3.42 0 00.806 1.946 3.42 3.42 0 010 4.438 3.42 3.42 0 00-.806 1.946 3.42 3.42 0 01-3.138 3.138 3.42 3.42 0 00-1.946.806 3.42 3.42 0 01-4.438 0 3.42 3.42 0 00-1.946-.806 3.42 3.42 0 01-3.138-3.138 3.42 3.42 0 00-.806-1.946 3.42 3.42 0 010-4.438 3.42 3.42 0 00.806-1.946 3.42 3.42 0 013.138-3.138z" />
            </svg>
            Generate {{ finalNames.length }} Certificate{{ finalNames.length === 1 ? '' : 's' }}
          </button>
        </div>
        <p v-if="skippedNoEmailCount" class="text-[11px] text-gray-400">
          {{ skippedNoEmailCount }} selected {{ skippedNoEmailCount === 1 ? 'person has' : 'people have' }} no email on file and will be skipped by Email (still included in Generate).
        </p>
      </div>
    </template>

    <!-- Preview & edit email modal (both per-row Send and bulk Email open this) -->
    <div v-if="emailModal" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50" @click.self="closeEmailModal">
      <div class="bg-white rounded-2xl shadow-xl w-full max-w-2xl max-h-[90vh] overflow-y-auto">
        <div class="px-5 py-4 border-b border-gray-100 flex items-center justify-between sticky top-0 bg-white z-10">
          <div>
            <div class="font-bold text-gray-800">Preview &amp; Edit Certificate Email</div>
            <p class="text-xs text-gray-500 mt-0.5">
              {{ emailModal.recipients.length === 1 ? `To ${emailModal.recipients[0].email}` : `${emailModal.recipients.length} recipients` }}
              — use <code class="bg-gray-100 px-1 rounded">{{ mergeTagExample }}</code> and <code class="bg-gray-100 px-1 rounded">{{ mergeTagEventExample }}</code> in Subject/Message to personalize each one.
            </p>
          </div>
          <button type="button" @click="closeEmailModal" class="text-gray-400 hover:text-gray-600 flex-shrink-0 ml-3">
            <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" d="M6 18L18 6M6 6l12 12"/></svg>
          </button>
        </div>

        <div class="p-5 space-y-4">
          <div v-if="emailModal.recipients.length > 1">
            <label class="block text-xs font-bold uppercase tracking-widest text-gray-400 mb-1.5">Previewing as</label>
            <select v-model="emailModal.previewKey" @change="refreshPreview"
              class="w-full border border-gray-200 rounded-xl px-3 py-2 text-sm focus:outline-none bg-white">
              <option v-for="p in emailModal.recipients" :key="p.key" :value="p.key">{{ p.name }} — {{ p.email }}</option>
            </select>
          </div>

          <div>
            <label class="block text-xs font-bold uppercase tracking-widest text-gray-400 mb-1.5">Subject</label>
            <input v-model="emailModal.subject" type="text"
              class="w-full border border-gray-200 rounded-xl px-3 py-2 text-sm focus:outline-none" />
          </div>
          <div>
            <label class="block text-xs font-bold uppercase tracking-widest text-gray-400 mb-1.5">Message (shown above the certificate)</label>
            <textarea v-model="emailModal.message" rows="5"
              class="w-full border border-gray-200 rounded-xl px-3 py-2 text-sm focus:outline-none"></textarea>
            <p class="text-[11px] text-gray-400 mt-1">Leave blank to send just the certificate, no message text.</p>
          </div>

          <!-- Live preview — exactly what will be emailed -->
          <div class="rounded-xl border border-gray-200 overflow-hidden">
            <div class="px-4 py-2 bg-gray-50 border-b border-gray-100 text-xs font-semibold text-gray-500 uppercase tracking-wide">Email preview</div>
            <div class="p-4 space-y-3 bg-white">
              <div class="text-sm"><span class="text-gray-400">Subject: </span><span class="font-semibold text-gray-800">{{ resolvedPreview.subject }}</span></div>
              <div v-if="resolvedPreview.message" class="text-sm text-gray-700 whitespace-pre-line">{{ resolvedPreview.message }}</div>
              <div class="flex justify-center py-4 bg-gray-50 rounded-lg">
                <div v-if="emailModal.rendering" class="py-10"><SpinnerComponent /></div>
                <img v-else-if="emailModal.previewUrl" :src="emailModal.previewUrl" class="max-w-full rounded shadow-sm" style="max-height: 320px;" alt="Certificate preview" />
              </div>
              <p class="text-[11px] text-gray-400">
                Delivered as a PDF attachment (shown above as a preview) — most inboxes will also display this image directly in the message.
              </p>
              <div v-if="eventLinks.length" class="pt-2 border-t border-gray-100">
                <div class="text-xs font-bold text-gray-600 mb-1">Useful links</div>
                <ul class="text-sm space-y-0.5">
                  <li v-for="l in eventLinks" :key="l.id">
                    <a :href="l.link" target="_blank" class="hover:underline" style="color: rgb(0,150,180);">{{ l.name }}</a>
                  </li>
                </ul>
              </div>
            </div>
          </div>

          <div v-if="emailModal.error" class="p-3 rounded-xl text-sm text-red-700 bg-red-50 border border-red-200">{{ emailModal.error }}</div>
        </div>

        <div class="px-5 py-4 border-t border-gray-100 flex justify-end gap-2 sticky bottom-0 bg-white">
          <button type="button" @click="closeEmailModal" class="px-4 py-2 text-sm font-medium text-gray-600 hover:bg-gray-50 rounded-lg">Cancel</button>
          <button type="button" @click="confirmSendEmail" :disabled="emailModal.sending || emailModal.rendering"
            class="px-4 py-2 text-sm font-semibold text-white rounded-lg disabled:opacity-50"
            style="background-color: rgb(254,80,103);">
            {{ emailModal.sending
              ? (emailModal.recipients.length > 1 ? `Sending ${emailModal.progressDone}/${emailModal.progressTotal}…` : 'Sending…')
              : (emailModal.recipients.length > 1 ? `Send ${emailModal.recipients.length} Emails` : 'Send Email') }}
          </button>
        </div>
      </div>
    </div>

    <!-- Off-screen certificate used to render each recipient's image before
    upload (Send/Email) — parked far off-window so it's never visible. -->
    <div style="position: fixed; left: -99999px; top: 0; pointer-events: none;" aria-hidden="true">
      <CertificateSheet ref="renderSheet" :name="renderJob.name" :type="renderJob.type" uid="email-render" />
    </div>
  </div>
</template>

<script>
import axios from 'axios'
import HeaderView from '@/includes/Header.vue'
import CertificateSheet from '@/components/CertificateSheet.vue'
import SpinnerComponent from '@/components/Spinner.vue'
import { fetchData } from '@/services/apiService'
import { useAuthStore } from '@/store/authStore'
import { CERTIFICATE_TYPES, CERTIFICATE_JOB_KEY, certificateCategory, tidyName } from '@/utils/certificateTypes'

const API_URL = import.meta.env.VITE_API_URL
// A paid abstract presenter who doesn't appear anywhere in the programme book.
// They still count as a presenter (that's how the event page pairs "Abstract
// Presenters" with "Paid"), so they get their own filter chip rather than
// being folded into a session type they don't have.
const ABSTRACT_ONLY_CATEGORY = 'abstract only'
const ABSTRACT_ONLY_LABEL = 'Abstract presenter — no programme slot'
// Certificate images are rendered client-side (same markup as the print
// page) then uploaded — batch emailing hands them to the server a handful
// at a time rather than one giant request.
const EMAIL_BATCH_SIZE = 15
const DEFAULT_EMAIL_SUBJECT = 'Your Certificate of Participation — {{name}}'
const DEFAULT_EMAIL_MESSAGE = [
  'Dear {{name}},',
  '',
  'Please find attached a copy of your certificate for your successful participation in the {{event}}.',
  '',
  'We have also included links below to the event photos, as well as the shared presentations from both the plenary and breakout-room (abstract) sessions.',
  '',
  'If you do not see your abstract listed under the sessions, or your presentation is unavailable, kindly share it with us at admission@cosecsa.org or info@ecsaconm.org so we can add it and make it available to other delegates for wider dissemination.',
  '',
  'Warm regards,',
  'ECSACONM Secretariat',
].join('\n')

export default {
  name: 'CertificatesView',
  components: { HeaderView, CertificateSheet, SpinnerComponent },
  setup() {
    const authStore = useAuthStore()
    return { authStore }
  },
  data() {
    return {
      types: CERTIFICATE_TYPES,
      type: 'attendee',
      events: [],
      selectedEventId: '',
      isLoading: false,
      registrations: [],
      attendedRegIds: new Set(),
      programme: [],
      // Public Links (event page's Links tab) — appended to every
      // certificate email as a "Useful links" block.
      eventLinks: [],
      search: '',
      attendedOnly: false,
      categoryFilter: [],
      attendeeCategoryFilter: [],
      // Narrows the table to people who actually have an email on file — the
      // ones Email can act on. Applies to every tab.
      emailOnly: false,
      // person key -> true; kept per type so switching tabs doesn't lose ticks
      selections: { attendee: {}, presenter: {}, usher: {} },
      extraNames: '',
      // off-screen certificate used to rasterize each recipient's image
      // before upload — see renderCertificateImage()
      renderJob: { name: '', type: CERTIFICATE_TYPES.attendee },
      rowMsg: null,
      emailSuccess: '',
      // Preview & edit modal — opened by both the per-row Send button and
      // the bulk Email button (see openEmailModal()). null when closed.
      emailModal: null,
      // Referenced in the modal hint text — kept out of the template
      // literal because Vue's mustache parser can't handle a nested {{ }}
      // inside an interpolation.
      mergeTagExample: '{{name}}',
      mergeTagEventExample: '{{event}}',
    }
  },
  computed: {
    selected() {
      return this.selections[this.type]
    },
    sourceHint() {
      return {
        attendee: 'Other paid delegates — registered, paid (secretariat always counts as paid), and not a presenter, usher or secretariat member. Member State, Other Africa, Participant and Exhibitor registrations are all grouped as one "Delegate" category. Use the category buttons to narrow the list; tick "only scanned as attended" to limit it to people whose QR badge was scanned.',
        presenter: 'Everyone named in the conference programme (Presentations by Room and the plenary schedule) plus every paid abstract presenter, one row per person, cross-matched to their registration for an email.',
        usher: 'Ushers and secretariat/support staff — registered with either role, same certificate for both.',
      }[this.type]
    },
    // Lookup sets used to keep a presenter out of the delegate list, so they
    // never get mailed two certificates. Email is the reliable join (a
    // programme slot is matched to a registration server-side); the name set
    // is the fallback for presenters with no email on file.
    presenterEmails() {
      return new Set(this.presenters.map(p => (p.email || '').trim().toLowerCase()).filter(Boolean))
    },
    presenterNames() {
      return new Set(this.presenters.map(p => p.name.toLowerCase()))
    },
    people() {
      if (this.type === 'presenter') return this.presenters
      // A presenter shouldn't also show up (and get double-emailed) under
      // "other delegates" just because they also have a paid registration.
      const regs = this.registrations.filter(r => {
        const isSupport = this.isSupportRole(r)
        if (this.type === 'usher') return isSupport
        if (isSupport || !r.paid) return false
        if (this.isPresenter(r)) return false
        const cats = this.attendeeCategoryFilter
        if (cats.length && !cats.includes(this.roleLabel(r))) return false
        return !this.attendedOnly || this.attendedRegIds.has(r.id)
      })
      return regs.map(r => ({
        key: `reg-${r.id}`,
        name: tidyName([r.title, r.firstname, r.lastname].filter(Boolean).join(' ')),
        category: this.roleLabel(r),
        detail: r.country || '',
        email: r.email || '',
      })).sort((a, b) => a.name.localeCompare(b.name))
    },
    presenters() {
      // ONE presenter group, built from two sources:
      //  1. the conference programme (Rooms page) — everyone named in a
      //     plenary/oral/poster slot;
      //  2. paid abstract presenters — an accepted abstract's presenting
      //     author who has a paid registration, the same pairing the event
      //     page counts as "Abstract Presenters / Paid". Someone whose
      //     abstract was accepted but who never made it onto the programme
      //     still gets a presenter certificate this way.
      // Dedupe across both: by email where the programme entry was matched to
      // a registration, otherwise by name.
      const byKey = {}
      const addSlot = (person) => {
        const p = byKey[person.key]
        if (!p) {
          byKey[person.key] = {
            key: person.key, name: person.name, email: person.email,
            categories: new Set(), sessions: [], titles: [],
          }
          return byKey[person.key]
        }
        // An abstract-presenter registration is the authoritative email for
        // this person if the programme slot had none.
        if (!p.email && person.email) p.email = person.email
        return p
      }

      this.programme.forEach(e => {
        const name = tidyName(e.presenter_name)
        if (!name) return
        const email = (e.matched_email || '').trim().toLowerCase()
        const p = addSlot({
          key: email ? `email-${email}` : `prog-${name.toLowerCase()}`,
          name, email,
        })
        p.categories.add(e.category)
        p.sessions.push([e.day, e.session, e.category].filter(Boolean).join(' · '))
        const title = e.title || e.activity || e.role
        if (title) p.titles.push(title)
      })

      this.registrations
        .filter(r => r.is_abstract_presenter && r.paid)
        .forEach(r => {
          const name = tidyName([r.title, r.firstname, r.lastname].filter(Boolean).join(' '))
          if (!name) return
          const email = (r.email || '').trim().toLowerCase()
          // Same person as a programme slot? Then the slot's key (email-based
          // when matched, name-based otherwise) is what we have to land on.
          const existingKey = email && byKey[`email-${email}`]
            ? `email-${email}`
            : `prog-${name.toLowerCase()}`
          addSlot({ key: existingKey, name, email })
        })

      return Object.values(byKey)
        .map(p => {
          // An abstract presenter with no programme slot has no session type to
          // show — flag the source so they're still filterable and obvious.
          const categories = new Set(p.categories)
          if (!categories.size) categories.add(ABSTRACT_ONLY_CATEGORY)
          return {
            key: p.key,
            name: p.name,
            category: p.sessions.length ? p.sessions.join(', ') : ABSTRACT_ONLY_LABEL,
            categories,
            detail: p.titles.join(' | '),
            email: p.email,
          }
        })
        .filter(p => !this.categoryFilter.length || this.categoryFilter.some(c => p.categories.has(c)))
        .sort((a, b) => a.name.localeCompare(b.name))
    },
    presenterCategories() {
      const cats = new Set(this.programme.map(e => e.category).filter(Boolean))
      if (this.presenters.some(p => p.categories.has(ABSTRACT_ONLY_CATEGORY))) {
        cats.add(ABSTRACT_ONLY_CATEGORY)
      }
      return [...cats].sort()
    },
    attendeeCategories() {
      const counts = {}
      this.registrations.forEach(r => {
        if (this.isSupportRole(r) || !r.paid) return
        if (this.isPresenter(r)) return
        const name = this.roleLabel(r)
        counts[name] = (counts[name] || 0) + 1
      })
      return Object.keys(counts).sort().map(name => ({ name, count: counts[name] }))
    },
    // Filter chips for the Presenters tab. A presenter can sit in more than
    // one category, so these counts are "rows this chip would show" and won't
    // necessarily add up to the tab total.
    presenterCategories() {
      const counts = new Map()
      this.presenters.forEach(p => p.categories.forEach(c => {
        counts.set(c, (counts.get(c) || 0) + 1)
      }))
      return [...counts.entries()]
        .sort((a, b) => a[0].localeCompare(b[0]))
        .map(([name, count]) => ({ name, count }))
    },
    filteredPeople() {
      const term = this.search.trim().toLowerCase()
      return this.people.filter(p => {
        if (this.emailOnly && !p.email) return false
        if (!term) return true
        return p.name.toLowerCase().includes(term)
          || (p.email || '').toLowerCase().includes(term)
      })
    },
    // People on the current tab that have an email — drives the "only with
    // email" chip so the count is visible before you turn it on.
    withEmailCount() {
      return this.people.filter(p => !!p.email).length
    },
    allShownSelected() {
      return this.filteredPeople.length > 0 && this.filteredPeople.every(p => this.selected[p.key])
    },
    selectedCount() {
      return this.people.filter(p => this.selected[p.key]).length
    },
    finalNames() {
      const names = this.people.filter(p => this.selected[p.key]).map(p => p.name)
      this.extraNames.split('\n').forEach(n => names.push(tidyName(n)))
      const seen = new Set()
      return names.filter(n => {
        const k = n.toLowerCase()
        if (!n || seen.has(k)) return false
        seen.add(k)
        return true
      })
    },
    // Only registration/programme-linked people have a known email — typed
    // "Additional names" never do, and are excluded here (they still print
    // fine via Generate, just can't be emailed automatically).
    emailableSelected() {
      return this.people.filter(p => this.selected[p.key] && p.email)
    },
    skippedNoEmailCount() {
      const selectedNoEmail = this.people.filter(p => this.selected[p.key] && !p.email).length
      const extraCount = this.extraNames.split('\n').map(n => tidyName(n)).filter(Boolean).length
      return selectedNoEmail + extraCount
    },
    // {{event}} merge tag — the selected event's display name, same text
    // shown in the "Select Event" dropdown above.
    selectedEventName() {
      const ev = this.events.find(e => String(e.id) === String(this.selectedEventId))
      return ev ? ev.event : ''
    },
    // Subject/message with {{name}} resolved for whichever recipient is
    // currently selected in the "Previewing as" picker — recalculates as
    // the admin types, no re-render needed (only the certificate image
    // itself requires a re-render, see refreshPreview()).
    resolvedPreview() {
      const m = this.emailModal
      if (!m) return { subject: '', message: '' }
      const person = m.recipients.find(p => p.key === m.previewKey) || m.recipients[0]
      const name = person ? person.name : ''
      return {
        subject: this.renderTemplate(m.subject, name),
        message: this.renderTemplate(m.message, name),
      }
    },
  },
  mounted() {
    this.loadEvents()
  },
  methods: {
    api() {
      const api = axios.create({ baseURL: API_URL })
      if (this.authStore.accessToken) api.defaults.headers.common['Authorization'] = `Bearer ${this.authStore.accessToken}`
      return api
    },
    async loadEvents() {
      try {
        const res = await fetchData('events', 0, 100, '')
        this.events = res.data || []
        // ?event=<id> (from the event page's Certificates button) preselects the event
        const fromQuery = this.events.find(e => String(e.id) === String(this.$route.query.event))
        if (fromQuery) {
          this.selectedEventId = fromQuery.id
          this.loadPeople()
        } else if (this.events.length === 1) {
          this.selectedEventId = this.events[0].id
          this.loadPeople()
        }
      } catch (e) {
        console.error('Error loading events:', e)
      }
    },
    // Registrations come back a page at a time; the first response tells us the
    // total, so any remaining pages are all requested at once rather than one
    // after another.
    async fetchRegistrations(api, eventId) {
      const first = (await api.get(`/registrations/?event_id=${eventId}&skip=0&limit=1000`)).data
      const regs = first?.data || []
      const total = first?.total ?? regs.length
      const skips = []
      for (let skip = 1000; skip < total; skip += 1000) skips.push(skip)
      if (skips.length) {
        const pages = await Promise.all(
          skips.map(skip => api.get(`/registrations/?event_id=${eventId}&skip=${skip}&limit=1000`))
        )
        pages.forEach(p => regs.push(...(p.data?.data || [])))
      }
      return regs
    },

    // The four sources the page needs are independent, so they're fetched
    // concurrently — the page renders as soon as the slowest one lands rather
    // than the sum of all four. Each is optional: a failure in one (no
    // programme book yet, no attendance data) must not blank the page.
    async loadPeople() {
      this.registrations = []
      this.attendedRegIds = new Set()
      this.programme = []
      this.attendeeCategoryFilter = []
      this.categoryFilter = []
      this.emailOnly = false
      this.eventLinks = []
      this.selections = { attendee: {}, presenter: {}, usher: {} }
      if (!this.selectedEventId) return
      this.isLoading = true
      const api = this.api()
      const eventId = this.selectedEventId
      try {
        const [regs, attendance, programme, event] = await Promise.allSettled([
          this.fetchRegistrations(api, eventId),
          api.get(`/events/${eventId}/attendance`),
          api.get(`/programme`, { params: { event_id: eventId, limit: 5000 } }),
          api.get(`/events/${eventId}`),
        ])

        if (regs.status === 'fulfilled') this.registrations = regs.value
        else console.error('Error loading registrations:', regs.reason)

        if (attendance.status === 'fulfilled') {
          const att = attendance.value.data?.data || []
          this.attendedRegIds = new Set(att.map(a => a.registration_id))
          // Default to "attended only" once the QR scans have been used.
          this.attendedOnly = this.attendedRegIds.size > 0
        }

        if (programme.status === 'fulfilled') {
          this.programme = programme.value.data?.data || []
        } else {
          console.error('Error loading programme:', programme.reason)
        }

        // Public Links (event page's Links tab) — shown under the certificate
        // in the email preview; the actual send re-fetches these fresh
        // server-side rather than trusting this copy.
        if (event.status === 'fulfilled') {
          const links = event.value.data?.links || []
          this.eventLinks = links.filter(l => (l.access_level || 'public') === 'public')
        }
      } finally {
        this.isLoading = false
      }
    },
    setType(key) {
      this.type = key
      this.search = ''
      // Category chips are per-tab, so a chip left ticked on the tab you're
      // leaving would silently filter the tab you're arriving on.
      this.categoryFilter = []
      this.attendeeCategoryFilter = []
    },
    roleLabel(r) {
      return certificateCategory(r.participation_role)
    },
    presenterCategoryLabel(c) {
      return c === ABSTRACT_ONLY_CATEGORY ? 'abstract presenter' : c
    },
    // True when this registration belongs to someone already in the presenter
    // group, so they're only listed (and mailed) once, as a presenter.
    isPresenter(reg) {
      const email = (reg.email || '').trim().toLowerCase()
      if (email && this.presenterEmails.has(email)) return true
      return this.presenterNames.has(
        tidyName([reg.title, reg.firstname, reg.lastname].filter(Boolean).join(' ')).toLowerCase()
      )
    },
    // Support staff — ushers and secretariat get the same certificate, so
    // they're one group for this purpose even though they're two different
    // participation_role values.
    isSupportRole(r) {
      const role = (r.participation_role || '').toLowerCase()
      return role === 'usher' || role === 'secretariat'
    },
    toggleAttendeeCategory(c) {
      const i = this.attendeeCategoryFilter.indexOf(c)
      if (i >= 0) this.attendeeCategoryFilter.splice(i, 1)
      else this.attendeeCategoryFilter.push(c)
    },
    toggleCategory(c) {
      const i = this.categoryFilter.indexOf(c)
      if (i >= 0) this.categoryFilter.splice(i, 1)
      else this.categoryFilter.push(c)
    },
    toggle(key, on) {
      this.selections[this.type] = { ...this.selected, [key]: on || undefined }
    },
    toggleAllShown(on) {
      const next = { ...this.selected }
      this.filteredPeople.forEach(p => { next[p.key] = on || undefined })
      this.selections[this.type] = next
    },
    openPrint(job) {
      localStorage.setItem(CERTIFICATE_JOB_KEY, JSON.stringify(job))
      window.open(this.$router.resolve({ name: 'CertificatePrint' }).href, '_blank')
    },
    generate() {
      if (!this.finalNames.length) return
      this.openPrint({ type: this.type, names: this.finalNames, autoPrint: true })
    },
    preview() {
      this.openPrint({ type: this.type, names: ['Full Name'], autoPrint: false })
    },

    // html2canvas reads the live DOM, so the certificate webfonts must be
    // actually applied before rasterizing — otherwise it falls back to system
    // fonts and the 172px "Certificate" overlaps "OF PARTICIPATION".
    // document.fonts.ready alone can resolve before the @font-face-triggered
    // requests are issued, so load them explicitly first.
    async ensureCertFonts() {
      const faces = [
        "400 172px 'Alex Brush'",
        "700 50px 'Montserrat'",
        "400 29px 'Montserrat'",
        "600 63px 'Playfair Display'",
      ]
      await Promise.all(
        faces.map(f => document.fonts.load(f).catch(() => {}))
      )
      await document.fonts.ready
    },

    // ── Email the certificate ────────────────────────────────
    // Rasterizes the hidden CertificateSheet (same markup the print page
    // uses) to a JPEG blob via html2canvas, at full 1920x1080 resolution.
    async renderCertificateImage(name) {
      this.renderJob = { name, type: this.types[this.type] }
      await this.$nextTick()
      await this.ensureCertFonts()
      const sheet = this.$refs.renderSheet
      if (sheet && sheet.fitName) sheet.fitName()
      await this.$nextTick()
      const hcMod = await import('html2canvas')
      const html2canvas = hcMod.default || hcMod
      const canvas = await html2canvas(sheet.$el, {
        scale: 1, useCORS: true, backgroundColor: '#ffffff', logging: false,
        width: 1920, height: 1080,
      })
      return new Promise(resolve => canvas.toBlob(resolve, 'image/jpeg', 0.85))
    },

    // {{name}} → the given name, everywhere it appears in a subject/message
    // template. Kept intentionally simple (one merge tag) rather than a
    // full template engine.
    renderTemplate(str, name) {
      return (str || '')
        .split('{{name}}').join(name)
        .split('{{event}}').join(this.selectedEventName)
    },

    // Opens the preview/edit modal for one person (row Send) or several
    // (bulk Email) — nothing is sent until the admin reviews and confirms.
    openEmailModal(recipients) {
      if (!recipients.length || this.emailModal) return
      this.rowMsg = null
      this.emailSuccess = ''
      this.emailModal = {
        recipients,
        subject: DEFAULT_EMAIL_SUBJECT,
        message: DEFAULT_EMAIL_MESSAGE,
        previewKey: recipients[0].key,
        previewUrl: '',
        rendering: false,
        sending: false,
        progressDone: 0,
        progressTotal: recipients.length,
        error: '',
      }
      this.refreshPreview()
    },
    closeEmailModal() {
      if (this.emailModal?.previewUrl) URL.revokeObjectURL(this.emailModal.previewUrl)
      this.emailModal = null
    },
    // Re-renders the certificate preview image for whichever recipient is
    // currently picked in "Previewing as" — rendering is the expensive
    // part, so this only runs on open and on recipient change, not on every
    // keystroke. Only the JPEG is needed here; the PDF (what's actually
    // attached) is built at send time in doSendOne/doEmailBulk.
    async refreshPreview() {
      const m = this.emailModal
      if (!m) return
      const person = m.recipients.find(p => p.key === m.previewKey) || m.recipients[0]
      if (!person) return
      m.rendering = true
      try {
        const { jpegBlob } = await this.renderCertificateAssets(person.name)
        if (this.emailModal !== m) return // modal was closed/replaced meanwhile
        if (m.previewUrl) URL.revokeObjectURL(m.previewUrl)
        m.previewUrl = URL.createObjectURL(jpegBlob)
      } finally {
        if (this.emailModal === m) m.rendering = false
      }
    },

    async confirmSendEmail() {
      const m = this.emailModal
      if (!m || m.sending) return
      m.sending = true
      m.error = ''
      try {
        if (m.recipients.length === 1) {
          const p = m.recipients[0]
          await this.doSendOne(p, m.subject, m.message)
          this.emailSuccess = `Sent to ${p.email}.`
        } else {
          const { queued, skipped } = await this.doEmailBulk(m, m.subject, m.message)
          this.emailSuccess = `Queued ${queued} certificate email${queued === 1 ? '' : 's'}.` +
            (skipped ? ` ${skipped} skipped (no image/email matched).` : '')
        }
        this.closeEmailModal()
      } catch (e) {
        m.error = e.response?.data?.detail || 'Failed to send.'
      } finally {
        if (this.emailModal === m) m.sending = false
      }
    },

    // ── Email the certificate ────────────────────────────────
    // Rasterizes the hidden CertificateSheet (same markup the print page
    // uses) via html2canvas, once, then derives both:
    //  - jpegBlob: shown inline in the email body (what the recipient sees
    //    without opening anything — email clients can't render a PDF inline)
    //  - pdfBlob: a full-bleed single-page PDF at the certificate's exact
    //    1920x1080 design size — the actual file attached/kept, same
    //    approach as the per-room PDF export on the Rooms page.
    async renderCertificateAssets(name) {
      this.renderJob = { name, type: this.types[this.type] }
      await this.$nextTick()
      await this.ensureCertFonts()
      const sheet = this.$refs.renderSheet
      if (sheet && sheet.fitName) sheet.fitName()
      await this.$nextTick()
      const hcMod = await import('html2canvas')
      const html2canvas = hcMod.default || hcMod
      const canvas = await html2canvas(sheet.$el, {
        scale: 1, useCORS: true, backgroundColor: '#ffffff', logging: false,
        width: 1920, height: 1080,
      })
      const jpegBlob = await new Promise(resolve => canvas.toBlob(resolve, 'image/jpeg', 0.85))

      const jsMod = await import('jspdf')
      const JsPDF = jsMod.jsPDF || (jsMod.default && jsMod.default.jsPDF) || jsMod.default
      const pdf = new JsPDF({ unit: 'px', format: [1920, 1080], orientation: 'landscape', hotfixes: ['px_scaling'] })
      pdf.addImage(canvas.toDataURL('image/jpeg', 0.92), 'JPEG', 0, 0, 1920, 1080, undefined, 'FAST')
      const pdfBlob = pdf.output('blob')

      return { jpegBlob, pdfBlob }
    },

    async doSendOne(p, subjectTpl, messageTpl) {
      this.rowMsg = null
      const { jpegBlob, pdfBlob } = await this.renderCertificateAssets(p.name)
      const form = new FormData()
      form.append('recipient_email', p.email)
      form.append('recipient_name', p.name)
      form.append('event_id', this.selectedEventId)
      form.append('subject', this.renderTemplate(subjectTpl, p.name))
      form.append('message', this.renderTemplate(messageTpl, p.name))
      form.append('image', jpegBlob, 'certificate.jpg')
      form.append('pdf', pdfBlob, 'certificate.pdf')
      await this.api().post('/certificates/send', form)
      this.rowMsg = { key: p.key, ok: true, text: 'Sent' }
    },

    async doEmailBulk(modal, subjectTpl, messageTpl) {
      const recipients = modal.recipients
      let queued = 0
      let skipped = 0
      for (let start = 0; start < recipients.length; start += EMAIL_BATCH_SIZE) {
        const batch = recipients.slice(start, start + EMAIL_BATCH_SIZE)
        const form = new FormData()
        const manifest = []
        for (const p of batch) {
          const { jpegBlob, pdfBlob } = await this.renderCertificateAssets(p.name)
          const base = p.key.replace(/[^A-Za-z0-9_-]+/g, '_')
          const filename = `${base}.jpg`
          const pdfFilename = `${base}.pdf`
          form.append('images', jpegBlob, filename)
          form.append('pdfs', pdfBlob, pdfFilename)
          manifest.push({
            filename, pdf_filename: pdfFilename, email: p.email, name: p.name,
            subject: this.renderTemplate(subjectTpl, p.name),
            message: this.renderTemplate(messageTpl, p.name),
          })
          modal.progressDone++
        }
        form.append('manifest', JSON.stringify(manifest))
        form.append('event_id', this.selectedEventId)
        const res = await this.api().post('/certificates/send-bulk', form)
        queued += res.data?.queued || 0
        skipped += res.data?.skipped || 0
      }
      return { queued, skipped }
    },
  },
}
</script>
