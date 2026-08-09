<template>
  <div class="flex flex-col w-full max-w-7xl mx-auto pb-6 pt-2 space-y-0" style="min-height:calc(100vh - 80px);">

    <!-- ── Header ─────────────────────────────────────────────────────────── -->
    <div class="flex items-center gap-3 mb-5 flex-shrink-0 flex-wrap">
      <button @click="$router.push({ name: 'Abstracts' })"
        class="p-1.5 rounded-lg text-abbey-400 hover:text-abbey-700 hover:bg-mercury-100 transition">
        <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"/>
        </svg>
      </button>

      <div v-if="isLoading" class="h-7 w-64 bg-mercury-200 rounded animate-pulse"></div>
      <h1 v-else class="text-lg font-semibold text-abbey-800 flex-1 truncate">{{ abstract.title }}</h1>

      <span v-if="abstract.status" :class="statusBadgeClass(abstract.status)"
        class="px-3 py-1 rounded-full text-sm font-semibold capitalize flex-shrink-0">
        {{ abstract.status?.replace('_', ' ') }}
      </span>
      <span v-if="abstract.presentation_type"
        class="px-3 py-1 rounded-full text-sm font-semibold capitalize flex-shrink-0"
        :class="abstract.presentation_type === 'oral' ? 'bg-blue-100 text-blue-700' : 'bg-purple-100 text-purple-700'">
        {{ abstract.presentation_type }}
      </span>
    </div>

    <!-- Success / error banners -->
    <div v-if="successMsg"
      class="mb-4 p-3 px-4 rounded-xl text-sm bg-green-100 border border-green-300 text-green-800">
      {{ successMsg }}
    </div>
    <div v-if="errorMsg"
      class="mb-4 p-3 px-4 rounded-xl text-sm bg-red-100 border border-red-300 text-red-800">
      {{ errorMsg }}
    </div>

    <!-- ── Loading skeleton ───────────────────────────────────────────────── -->
    <div v-if="isLoading" class="flex-1 grid xl:grid-cols-3 gap-6">
      <div class="xl:col-span-1 space-y-4">
        <div class="bg-white rounded-2xl shadow p-5 h-48 animate-pulse bg-mercury-100"></div>
      </div>
      <div class="xl:col-span-2 space-y-4">
        <div class="bg-white rounded-2xl shadow p-5 h-32 animate-pulse bg-mercury-100"></div>
        <div class="bg-white rounded-2xl shadow p-5 h-48 animate-pulse bg-mercury-100"></div>
        <div class="bg-white rounded-2xl shadow p-5 h-64 animate-pulse bg-mercury-100"></div>
      </div>
    </div>

    <!-- ── Main grid ──────────────────────────────────────────────────────── -->
    <div v-else class="flex-1 grid grid-cols-1 xl:grid-cols-3 gap-6">

      <!-- ── LEFT panel (management) ─────────────────────────────────────── -->
      <div class="xl:col-span-1 space-y-5 order-2 xl:order-1">

        <!-- Update Status -->
        <div class="bg-white rounded-2xl shadow p-5">
          <h2 class="text-xs font-bold text-abbey-400 uppercase tracking-widest mb-3">Update Status</h2>
          <select v-model="newStatus"
            class="w-full px-3 py-2.5 border border-mercury-300 rounded-xl text-sm text-abbey-700 focus:outline-none focus:ring-2 focus:ring-bondi-blue-400 mb-3">
            <option value="submitted">Submitted</option>
            <option value="under_review">Under Review</option>
            <option value="accepted">Accepted</option>
            <option value="rejected">Rejected</option>
            <option value="revision_required">Revision Required</option>
          </select>
          <button @click="doUpdateStatus" :disabled="isUpdating"
            class="w-full px-4 py-2 text-white rounded-xl text-sm font-semibold hover:opacity-90 transition disabled:opacity-50 bg-bondi-blue-500">
            {{ isUpdating ? 'Saving…' : 'Save Status' }}
          </button>
          <p v-if="statusSaved" class="mt-2 text-green-600 text-xs text-center">Status updated ✓</p>
        </div>

        <!-- Submission details -->
        <div class="bg-white rounded-2xl shadow p-5 space-y-3 text-sm">
          <h2 class="text-xs font-bold text-abbey-400 uppercase tracking-widest mb-1">Submission Details</h2>
          <div>
            <span class="text-abbey-400 text-xs uppercase tracking-wide">Event</span>
            <p class="font-medium mt-0.5 text-abbey-700">{{ abstract.event || '—' }}</p>
          </div>
          <div>
            <span class="text-abbey-400 text-xs uppercase tracking-wide">Track</span>
            <p class="font-medium mt-0.5 text-abbey-700">{{ abstract.track || '—' }}</p>
          </div>
          <div>
            <span class="text-abbey-400 text-xs uppercase tracking-wide">Submitted By</span>
            <p class="font-medium mt-0.5 text-abbey-700">{{ abstract.submitter_name || '—' }}</p>
          </div>
          <div>
            <span class="text-abbey-400 text-xs uppercase tracking-wide">Submitted On</span>
            <p class="font-medium mt-0.5 text-abbey-700">{{ formatDate(abstract.created_at) }}</p>
          </div>
          <div v-if="abstract.word_count">
            <span class="text-abbey-400 text-xs uppercase tracking-wide">Word Count</span>
            <p class="font-medium mt-0.5 text-abbey-700">{{ abstract.word_count }}</p>
          </div>
        </div>

        <!-- Keywords -->
        <div v-if="abstract.keywords" class="bg-white rounded-2xl shadow p-5">
          <h2 class="text-xs font-bold text-abbey-400 uppercase tracking-widest mb-2">Keywords</h2>
          <p class="text-sm text-abbey-600 italic">{{ abstract.keywords }}</p>
        </div>

      </div>

      <!-- ── RIGHT panel (content) ─────────────────────────────────────────── -->
      <div class="xl:col-span-2 space-y-5 order-1 xl:order-2">

        <!-- Authors table -->
        <div class="bg-white rounded-2xl shadow p-6">
          <h2 class="font-semibold text-abbey-800 mb-4 flex items-center gap-2">
            Authors &amp; Co-Authors
            <span v-if="abstract.authors && abstract.authors.length"
              class="text-xs px-2 py-0.5 rounded-full font-semibold bg-bondi-blue-50 text-bondi-blue-600">
              {{ abstract.authors.length }}
            </span>
          </h2>
          <div class="overflow-x-auto">
            <table class="w-full text-sm border-collapse">
              <thead>
                <tr class="bg-mercury-50 text-abbey-400 text-xs uppercase tracking-wide">
                  <th class="px-3 py-2 text-left rounded-tl-lg">#</th>
                  <th class="px-3 py-2 text-left">Name</th>
                  <th class="px-3 py-2 text-left hidden sm:table-cell">Email</th>
                  <th class="px-3 py-2 text-left hidden lg:table-cell">Affiliation</th>
                  <th class="px-3 py-2 text-left hidden md:table-cell">Country</th>
                  <th class="px-3 py-2 text-left rounded-tr-lg">Presenting</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-mercury-100">
                <tr v-if="!abstract.authors || !abstract.authors.length">
                  <td colspan="6" class="px-3 py-4 text-center text-abbey-400 italic text-xs">No author data available</td>
                </tr>
                <tr v-for="(au, i) in sortedAuthors" :key="au.id || i"
                  class="hover:bg-mercury-50 transition-colors">
                  <td class="px-3 py-2.5 text-abbey-400 text-xs">{{ i + 1 }}</td>
                  <td class="px-3 py-2.5 font-medium text-abbey-800">
                    {{ [au.firstname, au.lastname].filter(Boolean).join(' ') || '—' }}
                  </td>
                  <td class="px-3 py-2.5 text-abbey-500 hidden sm:table-cell">
                    <a v-if="au.email" :href="`mailto:${au.email}`"
                      class="text-bondi-blue-500 hover:underline">{{ au.email }}</a>
                    <span v-else class="text-abbey-300">—</span>
                  </td>
                  <td class="px-3 py-2.5 text-abbey-500 hidden lg:table-cell text-xs">
                    {{ au.affiliation || '—' }}
                  </td>
                  <td class="px-3 py-2.5 text-abbey-500 hidden md:table-cell text-xs">
                    {{ au.country || '—' }}
                  </td>
                  <td class="px-3 py-2.5">
                    <span v-if="au.is_presenting"
                      class="inline-flex items-center gap-1 bg-green-100 text-green-700 px-2 py-0.5 rounded-full text-xs font-semibold">
                      <svg class="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
                        <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"/>
                      </svg>
                      Presenter
                    </span>
                    <span v-else class="text-mercury-300 text-xs">—</span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- Abstract Body -->
        <div class="bg-white rounded-2xl shadow p-6">
          <h2 class="font-semibold text-abbey-800 mb-3">Abstract</h2>
          <div v-if="abstract.abstract_text"
            class="text-sm text-abbey-700 leading-relaxed whitespace-pre-wrap font-[inherit]">{{ abstract.abstract_text }}</div>
          <p v-else class="text-sm text-abbey-400 italic">No abstract body available for this submission.</p>
        </div>

        <!-- Reviewer assignments -->
        <div v-if="abstract.reviewer_assignments && abstract.reviewer_assignments.length"
          class="bg-white rounded-2xl shadow p-6">
          <h2 class="font-semibold text-abbey-800 mb-4 flex items-center gap-2">
            Review Assignments
            <span class="text-xs px-2 py-0.5 rounded-full font-medium bg-mercury-100 text-abbey-500">
              {{ abstract.reviewer_assignments.length }}
            </span>
          </h2>
          <div class="space-y-3">
            <div v-for="ra in abstract.reviewer_assignments" :key="ra.id"
              class="flex items-start justify-between px-4 py-3 rounded-xl border border-mercury-200 text-sm">
              <div class="min-w-0 flex-1">
                <p class="font-medium text-abbey-800 truncate">{{ ra.reviewer_name || '—' }}</p>
                <p class="text-abbey-400 text-xs mt-0.5 truncate">{{ ra.reviewer_email || '' }}</p>
              </div>
              <span :class="ra.completed ? 'bg-green-100 text-green-700' : 'bg-amber-100 text-amber-700'"
                class="ml-3 flex-shrink-0 px-2 py-0.5 rounded-full text-xs font-semibold">
                {{ ra.completed ? '✓ Reviewed' : '⏳ Pending' }}
              </span>
            </div>
          </div>
        </div>

      </div>
    </div>
  </div>
</template>

<script>
import { fetchItem, updateItem } from "@/services/apiService";
import { useAuthStore } from "@/store/authStore";

export default {
  name: 'AbstractView',
  data() {
    return {
      id: this.$route.params.id,
      isLoading: true,
      isUpdating: false,
      abstract: {},
      newStatus: '',
      successMsg: '',
      errorMsg: '',
      statusSaved: false,
    };
  },
  computed: {
    sortedAuthors() {
      if (!this.abstract.authors) return [];
      return [...this.abstract.authors].sort((a, b) => (a.author_order || 0) - (b.author_order || 0));
    },
  },
  setup() {
    const authStore = useAuthStore();
    const raw = authStore.permissions || [];
    const permissions = raw.map(p => typeof p === 'string' ? p : p.permission_code);
    return { permissions };
  },
  mounted() {
    this.getAbstract();
  },
  methods: {
    async getAbstract() {
      this.isLoading = true;
      try {
        const response = await fetchItem('abstracts', this.id);
        this.abstract = response.data || response;
        this.newStatus = this.abstract.status || '';
      } catch (err) {
        console.error('Error fetching abstract:', err);
        this.errorMsg = 'Failed to load abstract.';
      } finally {
        this.isLoading = false;
      }
    },
    async doUpdateStatus() {
      this.isUpdating = true;
      this.successMsg = '';
      this.errorMsg = '';
      this.statusSaved = false;
      try {
        await updateItem('abstracts', `${this.id}/status`, { status: this.newStatus });
        this.abstract.status = this.newStatus;
        this.statusSaved = true;
        setTimeout(() => this.statusSaved = false, 3000);
      } catch (err) {
        this.errorMsg = err.response?.data?.detail || 'Failed to update status.';
      } finally {
        this.isUpdating = false;
      }
    },
    formatDate(dateString) {
      if (!dateString) return '—';
      return new Date(dateString).toLocaleDateString('en-GB', {
        day: 'numeric', month: 'short', year: 'numeric',
      });
    },
    statusBadgeClass(status) {
      return {
        submitted:        'bg-yellow-100 text-yellow-700',
        pending:          'bg-yellow-100 text-yellow-700',
        under_review:     'bg-blue-100 text-blue-700',
        accepted:         'bg-green-100 text-green-700',
        approved:         'bg-green-100 text-green-700',
        rejected:         'bg-red-100 text-red-700',
        revision_required:'bg-orange-100 text-orange-700',
      }[status] || 'bg-mercury-100 text-abbey-600';
    },
  },
};
</script>
