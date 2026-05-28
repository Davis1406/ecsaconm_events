<template>
  <div class="flex flex-col space-y-6 flex-1">
    <div class="text-2xl font-bold text-gray-800">My Abstracts</div>

    <!-- Spinner -->
    <div v-if="isLoading" class="flex justify-center py-16">
      <svg class="animate-spin h-10 w-10" style="color: rgb(254,80,103);" fill="none" viewBox="0 0 24 24">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"/>
      </svg>
    </div>

    <div v-else class="bg-white rounded-2xl shadow-sm overflow-hidden">
      <!-- Empty state -->
      <div v-if="abstracts.length === 0" class="flex flex-col items-center justify-center py-20 text-center px-6">
        <div class="h-16 w-16 rounded-full flex items-center justify-center mb-4"
          style="background-color: rgba(254,80,103,0.1);">
          <svg class="w-8 h-8" style="color: rgb(254,80,103);" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
              d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
        </div>
        <p class="text-gray-500 text-base mb-1">No abstracts submitted yet.</p>
        <p class="text-gray-400 text-sm">Abstract submissions will appear here once available.</p>
      </div>

      <!-- Abstracts list -->
      <div v-else class="divide-y divide-gray-100">
        <div v-for="abstract in abstracts" :key="abstract.id" class="p-6 space-y-3">
          <div class="flex sm:flex-row flex-col sm:justify-between sm:items-start items-start gap-2">
            <div class="flex-1">
              <h2 class="font-semibold text-gray-800 text-base">{{ abstract.title }}</h2>
              <p class="text-gray-500 text-sm mt-1">
                {{ abstract.event }}
                <span v-if="abstract.track" class="text-gray-400"> &bull; {{ abstract.track }}</span>
              </p>
              <p class="text-xs text-gray-400 mt-1">
                Submitted {{ formatDate(abstract.created_at) }}
              </p>
            </div>
            <span :class="statusBadgeClass(abstract.status)"
              class="px-3 py-1 rounded-full text-xs font-semibold capitalize flex-shrink-0">
              {{ abstract.status }}
            </span>
          </div>

          <div v-if="abstract.authors && abstract.authors.length" class="flex flex-wrap gap-2">
            <span v-for="(au, i) in abstract.authors" :key="i"
              class="inline-flex items-center gap-1 text-xs bg-gray-100 text-gray-600 px-2.5 py-1 rounded-full">
              {{ au.firstname }} {{ au.lastname }}
              <span v-if="au.is_presenting"
                class="text-white text-xs px-1.5 py-0.5 rounded ml-1"
                style="background-color: rgb(254,80,103);">Presenting</span>
            </span>
          </div>

          <div>
            <button @click="abstract._expanded = !abstract._expanded"
              class="text-sm font-medium transition hover:opacity-80"
              style="color: rgb(254,80,103);">
              {{ abstract._expanded ? 'Hide abstract ▲' : 'Show abstract ▼' }}
            </button>
            <div v-if="abstract._expanded"
              class="mt-3 text-gray-600 text-sm leading-relaxed border-t border-gray-100 pt-3 whitespace-pre-wrap">
              {{ abstract.abstract_text || abstract.body || abstract.content }}
              <p v-if="abstract.keywords" class="mt-3 text-xs text-gray-400">
                <strong>Keywords:</strong> {{ abstract.keywords }}
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { fetchData } from "@/services/apiService";
import { useAuthStore } from "@/store/authStore";

export default {
    name: 'MyAbstracts',
    data() {
        return {
            isLoading: true,
            abstracts: [],
        };
    },
    mounted() {
        this.getMyAbstracts();
    },
    setup() {
        const authStore = useAuthStore();
        const user = authStore.loginUser;
        return { user };
    },
    methods: {
        async getMyAbstracts() {
            try {
                const response = await fetchData("abstracts/my-submissions", 1, 100, "");
                const data = response.data || response || [];
                this.abstracts = data.map(a => ({ ...a, _expanded: false }));
            } catch (error) {
                console.error("Error fetching my abstracts:", error);
                this.abstracts = [];
            } finally {
                this.isLoading = false;
            }
        },
        formatDate(dateString) {
            if (!dateString) return '—';
            const date = new Date(dateString);
            return date.toLocaleString("en-UK", {
                day: "2-digit",
                month: "2-digit",
                year: "numeric",
            });
        },
        statusBadgeClass(status) {
            const classes = {
                'Pending': 'bg-yellow-100 text-yellow-700',
                'pending': 'bg-yellow-100 text-yellow-700',
                'submitted': 'bg-yellow-100 text-yellow-700',
                'Approved': 'bg-green-100 text-green-700',
                'approved': 'bg-green-100 text-green-700',
                'accepted': 'bg-green-100 text-green-700',
                'Rejected': 'bg-red-100 text-red-700',
                'rejected': 'bg-red-100 text-red-700',
                'under_review': 'bg-blue-100 text-blue-700',
            };
            return classes[status] || 'bg-gray-100 text-gray-600';
        },
    }
}
</script>
