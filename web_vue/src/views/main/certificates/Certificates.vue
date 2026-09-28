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
      <p class="text-gray-400 text-sm">Attendees, presenters and ushers are loaded from the event</p>
    </div>

    <!-- Spinner -->
    <div v-else-if="isLoading" class="flex justify-center py-12">
      <svg class="animate-spin h-8 w-8" style="color: rgb(254,80,103);" fill="none" viewBox="0 0 24 24">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"/>
      </svg>
    </div>

    <template v-else>
      <div class="bg-white rounded-2xl shadow-sm overflow-hidden">
        <!-- Toolbar -->
        <div class="px-5 py-4 border-b border-gray-50 flex flex-wrap items-center gap-3">
          <input v-model="search" type="text" placeholder="Search name…"
            class="flex-1 sm:max-w-xs border border-gray-200 rounded-xl px-3 py-2 text-sm focus:outline-none" />
          <label v-if="type === 'attendee'" class="inline-flex items-center gap-2 text-xs text-gray-600 font-medium">
            <input type="checkbox" v-model="attendedOnly" class="rounded border-gray-300" />
            Only participants scanned as attended
          </label>
          <template v-if="type === 'attendee'">
            <button v-for="c in attendeeCategories" :key="c.name" type="button" @click="toggleAttendeeCategory(c.name)"
              class="px-2.5 py-1.5 rounded-lg text-xs font-semibold capitalize transition"
              :class="attendeeCategoryFilter.includes(c.name) ? 'text-white' : 'bg-gray-50 text-gray-500 hover:bg-gray-100'"
              :style="attendeeCategoryFilter.includes(c.name) ? { backgroundColor: 'rgb(254,80,103)' } : {}">
              {{ c.name }} ({{ c.count }})
            </button>
          </template>
          <template v-if="type === 'presenter'">
            <button v-for="c in presenterCategories" :key="c" type="button" @click="toggleCategory(c)"
              class="px-2.5 py-1.5 rounded-lg text-xs font-semibold capitalize transition"
              :class="categoryFilter.includes(c) ? 'text-white' : 'bg-gray-50 text-gray-500 hover:bg-gray-100'"
              :style="categoryFilter.includes(c) ? { backgroundColor: 'rgb(254,80,103)' } : {}">
              {{ c }}
            </button>
          </template>
          <span class="text-xs text-gray-400 font-medium sm:ml-auto">
            {{ selectedCount }} selected · {{ filteredPeople.length }} shown
          </span>
        </div>

        <div class="overflow-x-auto max-h-[60vh] overflow-y-auto">
          <table class="min-w-full text-sm">
            <thead class="sticky top-0">
              <tr class="bg-gray-50 text-xs font-bold uppercase tracking-wider text-gray-500 border-b border-gray-100">
                <th class="px-3 py-3 text-left w-8">
                  <input type="checkbox" :checked="allShownSelected" @change="toggleAllShown($event.target.checked)"
                    class="rounded border-gray-300" title="Select all shown" />
                </th>
                <th class="px-3 py-3 text-left whitespace-nowrap">Name on certificate</th>
                <th class="px-3 py-3 text-left whitespace-nowrap">{{ type === 'presenter' ? 'Session' : 'Category' }}</th>
                <th class="px-3 py-3 text-left">{{ type === 'presenter' ? 'Presentation' : 'Country' }}</th>
                <th class="px-3 py-3 text-left whitespace-nowrap">Email</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="p in filteredPeople" :key="p.key" class="border-b border-gray-50 hover:bg-gray-50">
                <td class="px-3 py-2.5">
                  <input type="checkbox" :checked="!!selected[p.key]" @change="toggle(p.key, $event.target.checked)"
                    class="rounded border-gray-300" />
                </td>
                <td class="px-3 py-2.5 font-semibold text-gray-800 whitespace-nowrap">{{ p.name }}</td>
                <td class="px-3 py-2.5 text-gray-600 text-xs whitespace-nowrap capitalize">{{ p.category }}</td>
                <td class="px-3 py-2.5 text-gray-500 text-xs">{{ p.detail }}</td>
                <td class="px-3 py-2.5 whitespace-nowrap">
                  <button v-if="p.email" type="button" @click="sendOne(p)"
                    :disabled="sendingKey === p.key || emailBusy"
                    class="inline-flex items-center gap-1 px-2.5 py-1 rounded-lg text-xs font-semibold border transition disabled:opacity-40"
                    :class="rowMsg && rowMsg.key === p.key
                      ? (rowMsg.ok ? 'border-green-200 text-green-600' : 'border-red-200 text-red-500')
                      : 'border-gray-200 text-gray-600 hover:border-pink-300 hover:text-pink-500'"
                    :title="p.email">
                    <svg v-if="sendingKey === p.key" class="animate-spin w-3.5 h-3.5" fill="none" viewBox="0 0 24 24">
                      <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
                      <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"/>
                    </svg>
                    <svg v-else class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                      <path stroke-linecap="round" stroke-linejoin="round" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"/>
                    </svg>
                    {{ rowMsg && rowMsg.key === p.key ? rowMsg.text : 'Send' }}
                  </button>
                  <span v-else class="text-xs text-gray-300 italic" title="No email on file">no email</span>
                </td>
              </tr>
            </tbody>
          </table>
          <div v-if="filteredPeople.length === 0" class="py-16 text-center">
            <p class="text-gray-400 text-sm italic">No one matches — you can still type names below.</p>
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
        <div v-if="emailError" class="p-3 rounded-xl text-sm text-red-700 bg-red-50 border border-red-200">{{ emailError }}</div>
        <div v-if="emailSuccess" class="p-3 rounded-xl text-sm text-green-700 bg-green-50 border border-green-200">{{ emailSuccess }}</div>
        <div v-if="emailProgress" class="p-3 rounded-xl text-sm text-gray-600 bg-gray-50 border border-gray-200">
          {{ emailProgress.phase }} certificate{{ emailProgress.total === 1 ? '' : 's' }}… {{ emailProgress.done }} of {{ emailProgress.total }}
        </div>

        <div class="flex flex-wrap items-center gap-3">
          <p class="text-xs text-gray-400 flex-1">
            <strong>Generate</strong> opens a print tab — choose <strong>Save as PDF</strong> and turn on
            <strong>Background graphics</strong> for one PDF with a page per person.
            <strong>Email</strong> sends each selected person their own certificate at their registration email
            (embedded in the message) — people typed under "Additional names" have no email on file and are skipped.
            ALL-CAPS / lowercase names are tidied to Title Case.
          </p>
          <button type="button" @click="emailSelected" :disabled="!emailableSelected.length || emailBusy || sendingKey"
            class="inline-flex items-center gap-1.5 px-5 py-2.5 rounded-xl text-sm font-semibold border-2 transition disabled:opacity-40"
            style="border-color: rgb(254,80,103); color: rgb(254,80,103);">
            <svg v-if="emailBusy" class="animate-spin w-4 h-4" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"/>
            </svg>
            <svg v-else class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"/>
            </svg>
            {{ emailBusy ? 'Sending…' : `Email ${emailableSelected.length} Certificate${emailableSelected.length === 1 ? '' : 's'}` }}
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
import { fetchData } from '@/services/apiService'
import { useAuthStore } from '@/store/authStore'
import { CERTIFICATE_TYPES, CERTIFICATE_JOB_KEY, tidyName } from '@/utils/certificateTypes'

const API_URL = import.meta.env.VITE_API_URL
// Certificate images are rendered client-side (same markup as the print
// page) then uploaded — batch emailing hands them to the server a handful
// at a time rather than one giant request.
const EMAIL_BATCH_SIZE = 15

export default {
  name: 'CertificatesView',
  components: { HeaderView, CertificateSheet },
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
      search: '',
      attendedOnly: false,
      categoryFilter: [],
      attendeeCategoryFilter: [],
      // person key -> true; kept per type so switching tabs doesn't lose ticks
      selections: { attendee: {}, presenter: {}, usher: {} },
      extraNames: '',
      // off-screen certificate used to rasterize each recipient's image
      // before upload — see renderCertificateImage()
      renderJob: { name: '', type: CERTIFICATE_TYPES.attendee },
      sendingKey: null,
      rowMsg: null,
      emailBusy: false,
      emailError: '',
      emailSuccess: '',
      emailProgress: null,
    }
  },
  computed: {
    selected() {
      return this.selections[this.type]
    },
    sourceHint() {
      return {
        attendee: 'Participants who have paid (secretariat counts as paid), in every category except ushers. Use the category buttons to narrow the list; tick "only scanned as attended" to limit it to people whose QR badge was scanned.',
        presenter: 'Presenters named in the conference programme (plenary, oral and poster), one row per person.',
        usher: 'Participants registered with the Usher role.',
      }[this.type]
    },
    people() {
      if (this.type === 'presenter') return this.presenters
      const regs = this.registrations.filter(r => {
        const isUsher = (r.participation_role || '').toLowerCase() === 'usher'
        if (this.type === 'usher') return isUsher
        if (isUsher || !r.paid) return false
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
      // One row per distinct presenter name (a presenter can appear in several slots).
      const byName = {}
      this.programme.forEach(e => {
        const name = tidyName(e.presenter_name)
        if (!name) return
        const key = `prog-${name.toLowerCase()}`
        if (!byName[key]) {
          byName[key] = { key, name, categories: new Set(), sessions: [], titles: [], email: '' }
        }
        const p = byName[key]
        p.categories.add(e.category)
        p.sessions.push([e.day, e.session, e.category].filter(Boolean).join(' · '))
        const title = e.title || e.activity || e.role
        if (title) p.titles.push(title)
        // presenter's registration email, matched server-side by name — every
        // slot sharing this name should match the same person, so keep the
        // first one found.
        if (!p.email && e.matched_email) p.email = e.matched_email
      })
      return Object.values(byName)
        .filter(p => !this.categoryFilter.length || this.categoryFilter.some(c => p.categories.has(c)))
        .map(p => ({
          key: p.key,
          name: p.name,
          category: p.sessions.join(', '),
          detail: p.titles.join(' | '),
          email: p.email,
        }))
        .sort((a, b) => a.name.localeCompare(b.name))
    },
    attendeeCategories() {
      const counts = {}
      this.registrations.forEach(r => {
        if ((r.participation_role || '').toLowerCase() === 'usher' || !r.paid) return
        const name = this.roleLabel(r)
        counts[name] = (counts[name] || 0) + 1
      })
      return Object.keys(counts).sort().map(name => ({ name, count: counts[name] }))
    },
    presenterCategories() {
      return [...new Set(this.programme.map(e => e.category).filter(Boolean))].sort()
    },
    filteredPeople() {
      const term = this.search.trim().toLowerCase()
      return term ? this.people.filter(p => p.name.toLowerCase().includes(term)) : this.people
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
    async loadPeople() {
      this.registrations = []
      this.attendedRegIds = new Set()
      this.programme = []
      this.attendeeCategoryFilter = []
      this.selections = { attendee: {}, presenter: {}, usher: {} }
      if (!this.selectedEventId) return
      this.isLoading = true
      const api = this.api()
      const eventId = this.selectedEventId
      try {
        const first = (await api.get(`/registrations/?event_id=${eventId}&skip=0&limit=1000`)).data
        let regs = first?.data || []
        const total = first?.total ?? regs.length
        for (let skip = 1000; skip < total; skip += 1000) {
          const page = await api.get(`/registrations/?event_id=${eventId}&skip=${skip}&limit=1000`)
          regs = regs.concat(page.data?.data || [])
        }
        this.registrations = regs

        try {
          const att = (await api.get(`/events/${eventId}/attendance`)).data?.data || []
          this.attendedRegIds = new Set(att.map(a => a.registration_id))
          // Default to "attended only" once the QR scans have been used.
          this.attendedOnly = this.attendedRegIds.size > 0
        } catch (e) { /* no attendance data */ }

        try {
          this.programme = (await api.get(`/programme`, { params: { event_id: eventId, limit: 5000 } })).data?.data || []
        } catch (e) { /* no programme for this event */ }
      } catch (e) {
        console.error('Error loading certificate recipients:', e)
      } finally {
        this.isLoading = false
      }
    },
    setType(key) {
      this.type = key
      this.search = ''
    },
    roleLabel(r) {
      return (r.participation_role || 'delegate').replace(/_/g, ' ')
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

    // ── Email the certificate ────────────────────────────────
    // Rasterizes the hidden CertificateSheet (same markup the print page
    // uses) to a JPEG blob via html2canvas, at full 1920x1080 resolution.
    async renderCertificateImage(name) {
      this.renderJob = { name, type: this.types[this.type] }
      await this.$nextTick()
      await document.fonts.ready
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

    async sendOne(p) {
      if (!p.email || this.sendingKey || this.emailBusy) return
      this.sendingKey = p.key
      this.rowMsg = null
      try {
        const blob = await this.renderCertificateImage(p.name)
        const form = new FormData()
        form.append('recipient_email', p.email)
        form.append('recipient_name', p.name)
        form.append('subject', `Your certificate — ${p.name}`)
        form.append('image', blob, 'certificate.jpg')
        await this.api().post('/certificates/send', form)
        this.rowMsg = { key: p.key, ok: true, text: 'Sent' }
      } catch (e) {
        this.rowMsg = { key: p.key, ok: false, text: e.response?.data?.detail || 'Failed to send' }
      } finally {
        this.sendingKey = null
      }
    },

    async emailSelected() {
      const recipients = this.emailableSelected
      if (!recipients.length || this.emailBusy || this.sendingKey) return
      this.emailBusy = true
      this.emailError = ''
      this.emailSuccess = ''
      this.emailProgress = { phase: 'Rendering', done: 0, total: recipients.length }
      let queued = 0
      let skipped = 0
      try {
        for (let start = 0; start < recipients.length; start += EMAIL_BATCH_SIZE) {
          const batch = recipients.slice(start, start + EMAIL_BATCH_SIZE)
          const form = new FormData()
          const manifest = []
          for (const p of batch) {
            const blob = await this.renderCertificateImage(p.name)
            const filename = `${p.key.replace(/[^A-Za-z0-9_-]+/g, '_')}.jpg`
            form.append('images', blob, filename)
            manifest.push({ filename, email: p.email, name: p.name })
            this.emailProgress.done++
          }
          form.append('manifest', JSON.stringify(manifest))
          this.emailProgress.phase = 'Sending'
          const res = await this.api().post('/certificates/send-bulk', form)
          queued += res.data?.queued || 0
          skipped += res.data?.skipped || 0
          this.emailProgress.phase = 'Rendering'
        }
        this.emailSuccess = `Queued ${queued} certificate email${queued === 1 ? '' : 's'}.` +
          (skipped ? ` ${skipped} skipped (no image/email matched).` : '')
      } catch (e) {
        this.emailError = e.response?.data?.detail || 'Failed to send certificate emails.'
      } finally {
        this.emailBusy = false
        this.emailProgress = null
      }
    },
  },
}
</script>
