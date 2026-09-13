<template>
  <div class="flex flex-col space-y-4 flex-1">
    <HeaderView :headerTitle="'Programme Summary'" />

    <!-- Flash messages -->
    <div v-if="flashMsg" class="px-3 py-2 rounded-md text-sm"
      :class="flashErr ? 'bg-red-50 text-red-600' : 'bg-green-50 text-green-600'">
      {{ flashMsg }}
    </div>

    <!-- KPI cards -->
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
      <div class="stat-card">
        <div class="stat-label">Total in Programme</div>
        <div class="stat-value">{{ filtered.length }}</div>
        <div class="mt-1 text-xs text-gray-500">{{ sessionWord }}</div>
      </div>
      <div class="stat-card stat-card--active" style="border-left: 4px solid #16a34a;">
        <div class="stat-label text-green-700">Registered &amp; Paid</div>
        <div class="stat-value text-green-700">{{ statusCount('paid') }}</div>
      </div>
      <div class="stat-card" style="border-left: 4px solid #d97706;">
        <div class="stat-label text-amber-700">Registered, Unpaid</div>
        <div class="stat-value text-amber-700">{{ statusCount('unpaid') }}</div>
      </div>
      <div class="stat-card" style="border-left: 4px solid #ef4444;">
        <div class="stat-label text-red-700">Not Registered</div>
        <div class="stat-value text-red-700">{{ statusCount('not_registered') }}</div>
      </div>
    </div>

    <div class="flex justify-end">
      <button @click="openAdd"
        class="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-semibold text-white transition hover:opacity-90"
        style="background-color: rgb(254,80,103);">
        <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
          <path stroke-linecap="round" d="M12 4v16m8-8H4"/>
        </svg>
        Add presenter / empty slot
      </button>
    </div>

    <!-- Filters -->
    <div class="flex flex-wrap items-center gap-2">
      <div class="flex items-center gap-1 flex-wrap">
        <button v-for="c in categoryChips" :key="c.value"
          @click="setCategory(c.value)"
          class="chip"
          :class="activeCategory === c.value ? 'chip--active' : 'chip--idle'">
          {{ c.label }}
        </button>
      </div>
      <div class="w-px h-6 bg-gray-200 mx-1 hidden sm:block"></div>
      <div class="flex items-center gap-1 flex-wrap">
        <button v-for="d in dayChips" :key="d.value"
          @click="setDay(d.value)"
          class="chip"
          :class="activeDay === d.value ? 'chip--active' : 'chip--idle'">
          {{ d.label }}
        </button>
      </div>
      <div class="flex-1"></div>
      <search-component @search="handleSearch" :placeholder="'Search name, title or code'" />
    </div>

    <SpinnerComponent v-if="loading" />

    <div v-else class="space-y-5">
      <!-- Day blocks -->
      <div v-for="day in dayBlocks" :key="day.day"
        class="rounded-xl border border-surface-container-high bg-surface-container-lowest overflow-hidden">
        <div class="px-4 py-3 flex items-center justify-between border-b border-gray-100"
          :style="{ backgroundColor: dayColor(day.day) }">
          <div class="font-bold text-white">{{ day.day }}</div>
          <div class="text-xs text-white/90 font-medium">
            {{ day.total }} items · {{ day.paid }} paid · {{ day.unpaid }} unpaid · {{ day.not_registered }} not registered
          </div>
        </div>
        <div class="divide-y divide-gray-50">
          <div v-if="day.items.length === 0" class="px-4 py-6 text-center text-sm text-gray-400 italic">
            No items match this filter.
          </div>
          <div v-for="item in day.items" :key="item.id" class="px-4 py-3 flex items-start gap-3">
            <!-- status dot -->
            <div class="mt-1 w-2.5 h-2.5 rounded-full flex-shrink-0"
              :style="{ backgroundColor: statusDot(item) }"
              :title="statusLabel(item)"></div>
            <div class="flex-1 min-w-0">
              <!-- presenter name row -->
              <div class="flex flex-wrap items-center gap-x-2 gap-y-0.5">
                <span class="font-semibold text-sm">{{ item.presenter_name || '—' }}</span>
                <template v-if="item.is_substitution">
                  <span class="badge badge-sub">SUB</span>
                  <span v-if="item.original_presenter" class="text-xs text-gray-500">
                    presenting instead of {{ item.original_presenter }}
                  </span>
                </template>
                <span v-if="item.status === 'not_registered'" class="badge badge-warn"
                  title="Name in the programme was not matched to a registered person">
                  ⚠ name not matched
                </span>
              </div>
              <!-- code / session / room -->
              <div class="text-xs text-gray-500 mt-0.5 flex flex-wrap items-center gap-x-2 gap-y-0.5">
                <span v-if="item.category === 'plenary'" class="font-semibold uppercase tracking-wide text-cp-secondary">Plenary</span>
                <span v-else-if="item.category === 'oral'" class="font-semibold uppercase tracking-wide text-cp-tertiary">Oral</span>
                <span v-else class="font-semibold uppercase tracking-wide text-amber-600">Poster</span>
                <span v-if="item.code" class="font-mono">{{ item.code }}</span>
                <template v-if="item.category !== 'plenary'">
                  <span v-if="item.session">Session {{ item.session }}</span>
                  <span v-if="item.room">{{ item.room }}</span>
                </template>
              </div>
              <!-- title / activity -->
              <div class="text-sm text-on-surface mt-1">
                {{ item.category === 'plenary' ? (item.activity || item.title || '') : (item.title || '') }}
              </div>
              <div v-if="item.category === 'plenary' && item.role" class="text-xs text-gray-500 italic">
                {{ item.role }}
              </div>
              <div v-if="item.notes" class="text-xs text-amber-700 mt-1">{{ item.notes }}</div>
              <!-- status labels -->
              <div class="mt-1.5 flex flex-wrap items-center gap-1.5">
                <span class="badge" :class="statusBadgeClass(item)">{{ statusLabel(item) }}</span>
                <span v-if="item.matched_first && item.match_score < 6" class="badge badge-weak"
                  :title="'Matched to ' + item.matched_first + ' ' + (item.matched_last || '') + ' (' + item.match_score + ')'">
                  weak match
                </span>
                <span v-if="item.presentation_file" class="badge badge-file" title="Slides uploaded">
                  📊 slides
                </span>
              </div>
            </div>
            <!-- actions -->
            <div class="flex items-center gap-1">
              <button @click="openEdit(item)" title="Edit presenter / details"
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

    <!-- Edit / substitute modal -->
    <div v-if="editOpen" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/40" @click.self="closeEdit">
      <div class="bg-white rounded-xl shadow-xl w-full max-w-lg max-h-[90vh] overflow-y-auto">
        <div class="px-5 py-4 border-b border-gray-100 flex items-center justify-between">
          <div>
            <div class="font-bold text-on-surface">{{ form.is_substitution ? 'Substitute Presenter' : (isAdd ? 'Add Presenter / Empty Slot' : 'Edit Programme Entry') }}</div>
            <div class="text-xs text-gray-500">
              <template v-if="isAdd">New oral programme entry</template>
              <template v-else>{{ form.category }} · {{ form.day }}<template v-if="form.code"> · {{ form.code }}</template></template>
            </div>
          </div>
          <button @click="closeEdit" class="text-gray-400 hover:text-gray-600">
            <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" d="M6 18L18 6M6 6l12 12"/></svg>
          </button>
        </div>
        <div class="p-5 space-y-3">
          <div>
            <label class="field-label">Presenter name</label>
            <input v-model.trim="form.presenter_name" type="text" class="field-input"
              placeholder="e.g. Jane Dlamini" />
          </div>
          <div>
            <label class="field-label">Title {{ editTarget.category === 'plenary' ? '(activity)' : '(presentation)' }}</label>
            <textarea v-model.trim="form.title" rows="2" class="field-input"
              placeholder="Presentation / activity title"></textarea>
          </div>
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div>
              <label class="field-label">Day</label>
              <select v-model="form.day" class="field-input">
                <option v-for="d in ['Day 1','Day 2','Day 3','Day 1-3']" :key="d">{{ d }}</option>
              </select>
            </div>
            <div>
              <label class="field-label">Room</label>
              <input v-model.trim="form.room" type="text" class="field-input"
                list="room-options" placeholder="e.g. GTCC 1, Jahazi 2, Main Hall" />
            </div>
          </div>
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div>
              <label class="field-label">Session</label>
              <select v-model="form.session" class="field-input">
                <option value="">—</option>
                <option v-for="s in ['S01','S02','S03','S04','S05','S06']" :key="s">{{ s }}</option>
              </select>
            </div>
            <div>
              <label class="field-label">Category</label>
              <select v-model="form.category" class="field-input">
                <option value="oral">Oral</option>
                <option value="poster">Poster</option>
                <option value="plenary">Plenary</option>
              </select>
            </div>
          </div>
          <!-- Substitution block -->
          <div class="rounded-lg border border-amber-200 bg-amber-50 p-3">
            <label class="flex items-center gap-2 text-sm font-medium text-amber-800 cursor-pointer">
              <input type="checkbox" v-model="form.is_substitution" class="accent-amber-600" />
              This person is a substitute presenter
            </label>
            <div v-if="form.is_substitution" class="mt-2">
              <label class="field-label">Presenting instead of (original presenter)</label>
              <input v-model.trim="form.original_presenter" type="text" class="field-input"
                placeholder="Scheduled presenter being replaced" />
            </div>
          </div>
          <div>
            <label class="field-label">Notes (optional)</label>
            <textarea v-model.trim="form.notes" rows="2" class="field-input"
              placeholder="Internal note visible to admins"></textarea>
          </div>
          <div v-if="saveErr" class="px-3 py-2 rounded-md bg-red-50 text-red-600 text-sm">{{ saveErr }}</div>
        </div>
        <div class="px-5 py-4 border-t border-gray-100 flex items-center justify-between">
          <button v-if="!isAdd" @click="removeEntry" class="text-sm text-red-600 hover:text-red-700 font-medium"
            :disabled="saving">
            Remove entry
          </button>
          <div v-else></div>
          <div class="flex items-center gap-2">
            <button @click="closeEdit" class="px-4 py-2 text-sm font-medium text-gray-600 hover:bg-gray-50 rounded-lg">
              Cancel
            </button>
            <button @click="saveEntry" :disabled="saving" class="px-4 py-2 text-sm font-semibold text-white rounded-lg transition"
              style="background-color: rgb(254,80,103);">
              {{ saving ? 'Saving…' : 'Save changes' }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <datalist id="room-options">
      <option value="Main Hall"></option>
      <option value="GTCC 1"></option>
      <option value="GTCC 2"></option>
      <option value="Jahazi 1"></option>
      <option value="Jahazi 2"></option>
    </datalist>
  </div>
</template>

<script>
import HeaderView from '@/includes/Header.vue'
import SpinnerComponent from '@/components/Spinner.vue'
import SearchComponent from '@/components/SearchComponent.vue'
import { useAuthStore } from '@/store/authStore'
import axios from 'axios'

const DAY_ORDER = ['Day 1', 'Day 2', 'Day 3', 'Day 1-3', 'Unassigned']

export default {
  name: 'ProgrammeSummaryView',
  components: { HeaderView, SpinnerComponent, SearchComponent },

  data() {
    return {
      entries: [],
      loading: true,
      flashMsg: '', flashErr: false,
      activeCategory: 'all',
      activeDay: 'all',
      searchPhrase: '',
      apiUrl: import.meta.env.VITE_API_URL,
      editOpen: false, editTarget: null, form: {}, saving: false, saveErr: '', isAdd: false,
      categoryChips: [
        { value: 'all', label: 'All' },
        { value: 'plenary', label: 'Plenary' },
        { value: 'oral', label: 'Oral' },
        { value: 'poster', label: 'Poster' },
      ],
      dayChips: [
        { value: 'all', label: 'All Days' },
        { value: 'Day 1', label: 'Day 1' },
        { value: 'Day 2', label: 'Day 2' },
        { value: 'Day 3', label: 'Day 3' },
        { value: 'Day 1-3', label: 'Poster Days' },
      ],
    }
  },

  setup() {
    const authStore = useAuthStore()
    return { accessToken: authStore.accessToken }
  },

  computed: {
    filtered() {
      const q = this.searchPhrase.trim().toLowerCase()
      return this.entries.filter(e => {
        if (this.activeCategory !== 'all' && e.category !== this.activeCategory) return false
        // Day 1-3 chip includes the poster block
        if (this.activeDay === 'Day 1-3') {
          if (e.day !== 'Day 1-3') return false
        } else if (this.activeDay !== 'all' && e.day !== this.activeDay) return false
        if (q) {
          const haystack = `${e.presenter_name} ${e.title} ${e.code} ${e.role} ${e.activity}`.toLowerCase()
          if (!haystack.includes(q)) return false
        }
        return true
      })
    },
    sessionWord() {
      if (this.activeDay !== 'all') return this.activeDay
      if (this.activeCategory !== 'all') return `All ${this.activeCategory} items`
      return 'Across all days'
    },
    dayBlocks() {
      const grouped = {}
      for (const e of this.filtered) {
        const day = e.day || 'Unassigned'
        ;(grouped[day] = grouped[day] || []).push(e)
      }
      return DAY_ORDER.filter(d => grouped[d]).map(day => {
        const items = grouped[day]
        return {
          day,
          items,
          total: items.length,
          paid: items.filter(i => i.status === 'registered_paid').length,
          unpaid: items.filter(i => i.status === 'registered_unpaid').length,
          not_registered: items.filter(i => i.status === 'not_registered').length,
        }
      })
    },
  },

  mounted() {
    this.load()
  },

  methods: {
    async load() {
      this.loading = true
      try {
        const res = await axios.get(`${this.apiUrl}/programme`, {
          params: { event_id: 1, limit: 1000 },
          headers: { Authorization: `Bearer ${this.accessToken}` },
        })
        this.entries = res.data.data || []
      } catch (e) {
        this.flash('Failed to load programme. ' + (e.response?.data?.detail || ''), true)
      } finally {
        this.loading = false
      }
    },

    statusCount(key) {
      return this.filtered.filter(i => {
        if (key === 'paid') return i.status === 'registered_paid'
        if (key === 'unpaid') return i.status === 'registered_unpaid'
        return i.status === 'not_registered'
      }).length
    },
    statusLabel(item) {
      return {
        registered_paid: 'Registered & Paid',
        registered_unpaid: 'Registered, Unpaid',
        not_registered: 'Not Registered',
      }[item.status] || item.status
    },
    statusDot(item) {
      return {
        registered_paid: '#16a34a',
        registered_unpaid: '#d97706',
        not_registered: '#ef4444',
      }[item.status] || '#9ca3af'
    },
    statusBadgeClass(item) {
      return {
        registered_paid: 'badge-paid',
        registered_unpaid: 'badge-unpaid',
        not_registered: 'badge-noreg',
      }[item.status] || 'badge'
    },

    setCategory(v) { this.activeCategory = v },
    setDay(v) { this.activeDay = v },
    handleSearch(q) { this.searchPhrase = q },

    dayColor(day) {
      return { 'Day 1': '#005988', 'Day 2': '#0a7ea4', 'Day 3': '#0d5c8a', 'Day 1-3': '#b45309', Unassigned: '#6b7280' }[day] || '#6b7280'
    },

    openEdit(item) {
      this.isAdd = false
      this.editTarget = item
      this.form = {
        category: item.category,
        day: item.day,
        session: item.session || '',
        room: item.room || '',
        code: item.code || '',
        title: item.title || '',
        presenter_name: item.presenter_name || '',
        role: item.role || '',
        activity: item.activity || '',
        original_presenter: item.original_presenter || '',
        is_substitution: !!item.is_substitution,
        notes: item.notes || '',
      }
      this.saveErr = ''
      this.editOpen = true
    },
    openAdd() {
      this.isAdd = true
      this.editTarget = null
      this.form = {
        category: 'oral',
        day: 'Day 1',
        session: 'S01',
        room: '',
        code: '',
        title: '',
        presenter_name: '',
        role: '',
        activity: '',
        original_presenter: '',
        is_substitution: false,
        notes: '',
      }
      this.saveErr = ''
      this.editOpen = true
    },
    closeEdit() {
      this.editOpen = false
      this.editTarget = null
    },
    async saveEntry() {
      if (!this.form.presenter_name.trim()) {
        this.saveErr = 'Presenter name is required.'
        return
      }
      this.saving = true
      this.saveErr = ''
      try {
        const payload = {
          presenter_name: this.form.presenter_name,
          title: this.form.title || null,
          day: this.form.day,
          session: this.form.session || null,
          room: this.form.room || null,
          category: this.form.category,
          original_presenter: this.form.is_substitution ? (this.form.original_presenter || null) : null,
          is_substitution: !!this.form.is_substitution,
          notes: this.form.notes || null,
        }
        let updated
        if (this.isAdd) {
          const res = await axios.post(`${this.apiUrl}/programme`, payload, {
            headers: { Authorization: `Bearer ${this.accessToken}` },
          })
          updated = res.data
          this.entries.push(updated)
        } else {
          const res = await axios.put(`${this.apiUrl}/programme/${this.editTarget.id}`, payload, {
            headers: { Authorization: `Bearer ${this.accessToken}` },
          })
          updated = res.data
          const idx = this.entries.findIndex(x => x.id === updated.id)
          if (idx >= 0) this.entries.splice(idx, 1, updated)
          else this.entries.push(updated)
        }
        this.closeEdit()
        this.flash(updated.is_substitution ? 'Substitution saved.' : (this.isAdd ? 'Entry added.' : 'Entry updated.'))
      } catch (e) {
        this.saveErr = e.response?.data?.detail || 'Save failed.'
      } finally {
        this.saving = false
      }
    },
    async removeEntry() {
      if (!confirm(`Remove "${this.editTarget.presenter_name}" from the programme?`)) return
      this.saving = true
      try {
        const id = this.editTarget.id
        await axios.delete(`${this.apiUrl}/programme/${id}`, {
          headers: { Authorization: `Bearer ${this.accessToken}` },
        })
        this.entries = this.entries.filter(x => x.id !== id)
        this.closeEdit()
        this.flash('Entry removed.')
      } catch (e) {
        this.saveErr = e.response?.data?.detail || 'Remove failed.'
      } finally {
        this.saving = false
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
.stat-card {
  @apply relative flex flex-col justify-center overflow-hidden rounded-xl border border-surface-container-high bg-surface-container-lowest p-5 text-left transition-all duration-150;
}
.stat-label {
  @apply text-[10px] font-bold uppercase tracking-wider text-on-surface-variant mb-1;
}
.stat-value {
  @apply text-4xl font-bold tracking-tight text-on-surface;
}
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
.badge-paid { @apply badge bg-green-100 text-green-700; }
.badge-unpaid { @apply badge bg-amber-100 text-amber-700; }
.badge-noreg { @apply badge bg-red-100 text-red-700; }
.badge-warn { @apply badge bg-orange-100 text-orange-700; }
.badge-sub { @apply badge bg-purple-100 text-purple-700; }
.badge-file { @apply badge bg-teal-100 text-teal-700; }
.badge-weak { @apply badge bg-yellow-100 text-yellow-700; }
.action-btn {
  @apply flex items-center justify-center w-8 h-8 rounded-lg border border-gray-200 bg-white text-gray-500 hover:bg-gray-50 transition-colors flex-shrink-0;
}
.field-label {
  @apply block text-xs font-bold uppercase tracking-wide text-on-surface-variant mb-1;
}
.field-input {
  @apply w-full rounded-lg border border-gray-200 bg-white px-3 py-2 text-sm text-on-surface focus:outline-none focus:ring-2 focus:ring-cp-secondary;
}
</style>