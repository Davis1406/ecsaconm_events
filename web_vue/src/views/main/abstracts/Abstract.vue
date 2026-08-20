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
      <h1 v-else class="text-lg font-semibold text-abbey-800 flex-1 min-w-0">
        <span v-if="!isEditing" class="truncate block">{{ abstract.title }}</span>
        <input v-else v-model="editForm.title"
          class="w-full px-3 py-1.5 border border-bondi-blue-300 rounded-xl text-base font-semibold text-abbey-800 focus:outline-none focus:ring-2 focus:ring-bondi-blue-400"
          placeholder="Abstract title" />
      </h1>

      <!-- Status badge (view only) -->
      <span v-if="abstract.status && !isEditing" :class="statusBadgeClass(abstract.status)"
        class="px-3 py-1 rounded-full text-sm font-semibold capitalize flex-shrink-0">
        {{ abstract.status?.replace('_', ' ') }}
      </span>
      <span v-if="abstract.presentation_type && !isEditing"
        class="px-3 py-1 rounded-full text-sm font-semibold capitalize flex-shrink-0"
        :class="abstract.presentation_type === 'oral' ? 'bg-blue-100 text-blue-700' : 'bg-purple-100 text-purple-700'">
        {{ abstract.presentation_type }}
      </span>

      <!-- Edit / Save / Cancel buttons -->
      <template v-if="!isLoading">
        <button v-if="!isEditing" @click="startEdit"
          class="inline-flex items-center gap-1.5 px-4 py-2 rounded-xl text-sm font-semibold border-2 border-bondi-blue-400 text-bondi-blue-600 hover:bg-bondi-blue-50 transition flex-shrink-0">
          <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
              d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"/>
          </svg>
          Edit
        </button>
        <template v-else>
          <button @click="saveEdit" :disabled="isSaving"
            class="inline-flex items-center gap-1.5 px-4 py-2 rounded-xl text-sm font-semibold text-white bg-bondi-blue-500 hover:bg-bondi-blue-600 transition disabled:opacity-50 flex-shrink-0">
            <svg v-if="isSaving" class="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"/>
            </svg>
            {{ isSaving ? 'Saving…' : 'Save Changes' }}
          </button>
          <button @click="cancelEdit"
            class="inline-flex items-center gap-1.5 px-4 py-2 rounded-xl text-sm font-semibold border border-mercury-300 text-abbey-600 hover:bg-mercury-50 transition flex-shrink-0">
            Cancel
          </button>
        </template>
      </template>
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

        <!-- Update Status (always visible) -->
        <div class="bg-white rounded-2xl shadow p-5">
          <h2 class="text-xs font-bold text-abbey-400 uppercase tracking-widest mb-3">Status</h2>
          <!-- In edit mode, bind to editForm.status; otherwise bind to newStatus for quick-save -->
          <select v-if="isEditing" v-model="editForm.status"
            class="w-full px-3 py-2.5 border border-mercury-300 rounded-xl text-sm text-abbey-700 focus:outline-none focus:ring-2 focus:ring-bondi-blue-400 mb-3">
            <option value="submitted">Submitted</option>
            <option value="under_review">Under Review</option>
            <option value="accepted">Accepted</option>
            <option value="rejected">Rejected</option>
            <option value="revision_required">Revision Required</option>
          </select>
          <select v-else v-model="newStatus"
            class="w-full px-3 py-2.5 border border-mercury-300 rounded-xl text-sm text-abbey-700 focus:outline-none focus:ring-2 focus:ring-bondi-blue-400 mb-3">
            <option value="submitted">Submitted</option>
            <option value="under_review">Under Review</option>
            <option value="accepted">Accepted</option>
            <option value="rejected">Rejected</option>
            <option value="revision_required">Revision Required</option>
          </select>
          <!-- Quick-save status only when not in full edit mode -->
          <button v-if="!isEditing" @click="doUpdateStatus" :disabled="isUpdating"
            class="w-full px-4 py-2 text-white rounded-xl text-sm font-semibold hover:opacity-90 transition disabled:opacity-50 bg-bondi-blue-500">
            {{ isUpdating ? 'Saving…' : 'Save Status' }}
          </button>
          <p v-if="statusSaved && !isEditing" class="mt-2 text-green-600 text-xs text-center">Status updated ✓</p>
        </div>

        <!-- Submission / meta details -->
        <div class="bg-white rounded-2xl shadow p-5 space-y-3 text-sm">
          <h2 class="text-xs font-bold text-abbey-400 uppercase tracking-widest mb-1">Details</h2>

          <!-- Presentation type (editable) -->
          <div>
            <span class="text-abbey-400 text-xs uppercase tracking-wide">Presentation Type</span>
            <div class="mt-0.5">
              <select v-if="isEditing" v-model="editForm.presentation_type"
                class="w-full px-3 py-2 border border-mercury-300 rounded-xl text-sm text-abbey-700 focus:outline-none focus:ring-2 focus:ring-bondi-blue-400">
                <option value="oral">Oral</option>
                <option value="poster">Poster</option>
                <option value="either">Either</option>
              </select>
              <p v-else class="font-medium text-abbey-700 capitalize">{{ abstract.presentation_type || '—' }}</p>
            </div>
          </div>

          <!-- Track (editable) -->
          <div>
            <span class="text-abbey-400 text-xs uppercase tracking-wide">Track</span>
            <div class="mt-0.5">
              <input v-if="isEditing" v-model="editForm.track"
                class="w-full px-3 py-2 border border-mercury-300 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-bondi-blue-400"
                placeholder="Track / theme" />
              <p v-else class="font-medium text-abbey-700">{{ abstract.track || '—' }}</p>
            </div>
          </div>

          <!-- Event (read-only) -->
          <div>
            <span class="text-abbey-400 text-xs uppercase tracking-wide">Event</span>
            <p class="font-medium mt-0.5 text-abbey-700">{{ abstract.event || '—' }}</p>
          </div>

          <!-- Submitted By (read-only) -->
          <div>
            <span class="text-abbey-400 text-xs uppercase tracking-wide">Submitted By</span>
            <p class="font-medium mt-0.5 text-abbey-700">{{ abstract.submitter_name || '—' }}</p>
          </div>

          <!-- Submitted On (read-only) -->
          <div>
            <span class="text-abbey-400 text-xs uppercase tracking-wide">Submitted On</span>
            <p class="font-medium mt-0.5 text-abbey-700">{{ formatDate(abstract.created_at) }}</p>
          </div>

          <div v-if="abstract.word_count">
            <span class="text-abbey-400 text-xs uppercase tracking-wide">Word Count</span>
            <p class="font-medium mt-0.5 text-abbey-700">{{ abstract.word_count }}</p>
          </div>
        </div>

        <!-- Keywords (editable) -->
        <div class="bg-white rounded-2xl shadow p-5">
          <h2 class="text-xs font-bold text-abbey-400 uppercase tracking-widest mb-2">Keywords</h2>
          <textarea v-if="isEditing" v-model="editForm.keywords" rows="3"
            class="w-full px-3 py-2 border border-mercury-300 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-bondi-blue-400 resize-none"
            placeholder="Comma-separated keywords"></textarea>
          <p v-else-if="abstract.keywords" class="text-sm text-abbey-600 italic">{{ abstract.keywords }}</p>
          <p v-else class="text-sm text-abbey-400 italic">No keywords.</p>
        </div>

      </div>

      <!-- ── RIGHT panel (content) ─────────────────────────────────────────── -->
      <div class="xl:col-span-2 space-y-5 order-1 xl:order-2">

        <!-- Authors table -->
        <div class="bg-white rounded-2xl shadow p-6">
          <div class="flex items-center justify-between mb-4">
            <h2 class="font-semibold text-abbey-800 flex items-center gap-2">
              Authors &amp; Co-Authors
              <span class="text-xs px-2 py-0.5 rounded-full font-semibold bg-bondi-blue-50 text-bondi-blue-600">
                {{ isEditing ? editForm.authors.length : (abstract.authors?.length || 0) }}
              </span>
            </h2>
            <button v-if="isEditing" @click="addAuthorRow"
              class="inline-flex items-center gap-1 px-3 py-1.5 rounded-xl text-xs font-semibold text-white bg-bondi-blue-500 hover:bg-bondi-blue-600 transition">
              <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/>
              </svg>
              Add Author
            </button>
          </div>

          <!-- VIEW MODE: authors table -->
          <div v-if="!isEditing" class="overflow-x-auto">
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
                  <td class="px-3 py-2.5 text-abbey-500 hidden lg:table-cell text-xs">{{ au.affiliation || '—' }}</td>
                  <td class="px-3 py-2.5 text-abbey-500 hidden md:table-cell text-xs">{{ au.country || '—' }}</td>
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

          <!-- EDIT MODE: authors editable rows -->
          <div v-else class="space-y-3">
            <div v-for="(au, i) in editForm.authors" :key="i"
              class="border border-mercury-200 rounded-xl p-3 bg-mercury-50 relative">
              <div class="flex items-center justify-between mb-2">
                <span class="text-xs font-bold text-abbey-500 uppercase tracking-wide">Author {{ i + 1 }}</span>
                <div class="flex items-center gap-2">
                  <label class="flex items-center gap-1.5 text-xs text-abbey-600 cursor-pointer">
                    <input type="checkbox" v-model="au.is_presenting"
                      class="rounded border-mercury-300 text-bondi-blue-500 focus:ring-bondi-blue-400" />
                    Presenter
                  </label>
                  <button @click="removeAuthorRow(i)" title="Remove author"
                    class="p-1 rounded-lg text-red-400 hover:text-red-600 hover:bg-red-50 transition">
                    <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
                    </svg>
                  </button>
                </div>
              </div>
              <div class="grid grid-cols-2 gap-2 sm:grid-cols-3">
                <input v-model="au.firstname" placeholder="First name"
                  class="px-2.5 py-1.5 border border-mercury-300 rounded-lg text-sm focus:outline-none focus:ring-1 focus:ring-bondi-blue-400 bg-white" />
                <input v-model="au.lastname" placeholder="Last name"
                  class="px-2.5 py-1.5 border border-mercury-300 rounded-lg text-sm focus:outline-none focus:ring-1 focus:ring-bondi-blue-400 bg-white" />
                <input v-model="au.email" placeholder="Email" type="email"
                  class="px-2.5 py-1.5 border border-mercury-300 rounded-lg text-sm focus:outline-none focus:ring-1 focus:ring-bondi-blue-400 bg-white col-span-2 sm:col-span-1" />
                <input v-model="au.affiliation" placeholder="Affiliation / Institution"
                  class="px-2.5 py-1.5 border border-mercury-300 rounded-lg text-sm focus:outline-none focus:ring-1 focus:ring-bondi-blue-400 bg-white col-span-2" />
                <input v-model="au.country" placeholder="Country"
                  class="px-2.5 py-1.5 border border-mercury-300 rounded-lg text-sm focus:outline-none focus:ring-1 focus:ring-bondi-blue-400 bg-white" />
              </div>
              <!-- Presenter highlight -->
              <div v-if="au.is_presenting" class="mt-2 flex items-center gap-1 text-xs text-green-600 font-medium">
                <svg class="w-3.5 h-3.5" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"/>
                </svg>
                Marked as presenter
              </div>
            </div>
            <div v-if="editForm.authors.length === 0" class="text-center text-abbey-400 text-sm italic py-4">
              No authors — click "Add Author" to add one.
            </div>
          </div>
        </div>

        <!-- Abstract Body -->
        <div class="bg-white rounded-2xl shadow p-6">
          <h2 class="font-semibold text-abbey-800 mb-3">Abstract</h2>
          <textarea v-if="isEditing" v-model="editForm.abstract_text" rows="14"
            class="w-full px-3 py-2.5 border border-mercury-300 rounded-xl text-sm text-abbey-700 focus:outline-none focus:ring-2 focus:ring-bondi-blue-400 leading-relaxed resize-y font-[inherit]"
            placeholder="Abstract body text…"></textarea>
          <div v-else-if="abstract.abstract_text"
            class="text-sm text-abbey-700 leading-relaxed whitespace-pre-wrap font-[inherit]">{{ abstract.abstract_text }}</div>
          <p v-else class="text-sm text-abbey-400 italic">No abstract body available for this submission.</p>
        </div>

        <!-- Reviewer assignments (read-only always) -->
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
      isSaving: false,
      isEditing: false,
      abstract: {},
      newStatus: '',
      successMsg: '',
      errorMsg: '',
      statusSaved: false,
      // Edit form mirror
      editForm: {
        title: '',
        abstract_text: '',
        track: '',
        keywords: '',
        presentation_type: '',
        status: '',
        authors: [],
      },
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

    startEdit() {
      // Deep-copy the current abstract into the edit form
      this.editForm = {
        title: this.abstract.title || '',
        abstract_text: this.abstract.abstract_text || '',
        track: this.abstract.track || '',
        keywords: this.abstract.keywords || '',
        presentation_type: this.abstract.presentation_type || 'oral',
        status: this.abstract.status || 'accepted',
        authors: this.sortedAuthors.map(au => ({
          firstname: au.firstname || '',
          lastname: au.lastname || '',
          email: au.email || '',
          affiliation: au.affiliation || '',
          country: au.country || '',
          is_presenting: !!au.is_presenting,
          author_order: au.author_order || 0,
        })),
      };
      this.successMsg = '';
      this.errorMsg = '';
      this.isEditing = true;
    },

    cancelEdit() {
      this.isEditing = false;
      this.successMsg = '';
      this.errorMsg = '';
    },

    addAuthorRow() {
      this.editForm.authors.push({
        firstname: '',
        lastname: '',
        email: '',
        affiliation: '',
        country: '',
        is_presenting: false,
        author_order: this.editForm.authors.length,
      });
    },

    removeAuthorRow(index) {
      this.editForm.authors.splice(index, 1);
    },

    async saveEdit() {
      this.isSaving = true;
      this.successMsg = '';
      this.errorMsg = '';
      try {
        const payload = {
          title: this.editForm.title.trim(),
          abstract_text: this.editForm.abstract_text.trim(),
          track: this.editForm.track.trim(),
          keywords: this.editForm.keywords.trim(),
          presentation_type: this.editForm.presentation_type,
          status: this.editForm.status,
          authors: this.editForm.authors.map((au, i) => ({
            firstname: au.firstname.trim(),
            lastname: au.lastname.trim(),
            email: au.email.trim().toLowerCase() || null,
            affiliation: au.affiliation.trim() || null,
            country: au.country.trim() || null,
            is_presenting: !!au.is_presenting,
            author_order: i,
          })),
        };
        const updated = await updateItem('abstracts', this.id, payload);
        this.abstract = updated.data || updated;
        this.newStatus = this.abstract.status || '';
        this.isEditing = false;
        this.successMsg = 'Abstract updated successfully.';
        setTimeout(() => { this.successMsg = ''; }, 4000);
      } catch (err) {
        this.errorMsg = err.response?.data?.detail || 'Failed to save changes.';
      } finally {
        this.isSaving = false;
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
