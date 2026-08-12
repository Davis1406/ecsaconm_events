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

          <!-- Upload presentation -->
          <div class="border-t border-gray-100 pt-4 mt-2">
            <p class="text-xs font-semibold uppercase tracking-wide text-gray-500 mb-2">Presentation File</p>

            <!-- Already uploaded -->
            <div v-if="abstract.presentation_file" class="flex items-center gap-3 mb-2">
              <span class="inline-flex items-center gap-1 text-xs text-green-700 bg-green-100 px-3 py-1 rounded-full font-semibold">
                ✓ Presentation uploaded
              </span>
              <span class="text-xs text-gray-400">{{ formatDate(abstract.presentation_uploaded_at) }}</span>
            </div>

            <div class="flex flex-col sm:flex-row gap-2 items-start sm:items-center">
              <input type="file"
                accept=".ppt,.pptx,.pdf,.zip,.mp4"
                @change="e => abstract._file = e.target.files[0]"
                class="text-sm text-gray-600 border border-gray-200 rounded-xl px-3 py-1.5
                       file:mr-3 file:py-1 file:px-3 file:rounded-full file:border-0
                       file:text-xs file:font-semibold file:text-white cursor-pointer"
                style="--tw-ring-color: rgb(254,80,103);" />
              <button
                @click="uploadPresentation(abstract)"
                :disabled="!abstract._file || abstract._uploading"
                class="px-4 py-1.5 text-xs rounded-full font-semibold text-white disabled:opacity-50 transition hover:opacity-90"
                style="background-color: rgb(254,80,103);">
                {{ abstract._uploading ? 'Uploading…' : (abstract.presentation_file ? 'Replace file' : 'Upload') }}
              </button>
            </div>
            <p class="text-xs text-gray-400 mt-1">Accepted: .pptx .ppt .pdf .zip .mp4 · Max 100 MB</p>
            <p v-if="abstract._uploadMsg" class="text-xs mt-1 font-medium"
              :class="abstract._uploadErr ? 'text-red-600' : 'text-green-600'">
              {{ abstract._uploadMsg }}
            </p>
          </div>

        </div>
      </div>
    </div>

    <!-- Presentation templates — only shown to paid, registered presenters -->
    <div v-if="isPaidPresenter" class="bg-white rounded-2xl shadow-sm overflow-hidden">
      <div class="px-6 py-5 border-b border-gray-100">
        <h3 class="font-semibold text-gray-800 mb-1">Presentation Templates</h3>
        <p class="text-sm text-gray-500">
          Official ECSACONM templates to help you prepare your slides — preview or download below.
        </p>
      </div>

      <div v-if="templatesLoading" class="px-6 py-8 text-center text-sm text-gray-400">Loading…</div>
      <div v-else-if="templates.length === 0" class="px-6 py-8 text-center text-sm text-gray-400 italic">
        No templates uploaded yet.
      </div>
      <div v-else class="divide-y divide-gray-100">
        <div v-for="tpl in templates" :key="tpl.id"
          class="flex items-center justify-between gap-3 px-6 py-3.5">
          <div class="min-w-0">
            <p class="text-sm font-medium text-gray-800 truncate">
              <span class="mr-1.5">{{ fileIcon(tpl.original_name) }}</span>{{ tpl.original_name }}
            </p>
            <p v-if="tpl.description" class="text-xs text-gray-400 truncate mt-0.5">{{ tpl.description }}</p>
          </div>
          <div class="flex items-center gap-1.5 flex-shrink-0">
            <button v-if="isPreviewable(tpl.original_name)" @click="openTemplatePreview(tpl)" title="Preview"
              class="tpl-action-btn" style="color: rgb(254,80,103);">
              <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                <path stroke-linecap="round" stroke-linejoin="round" d="M2.036 12.322a1.012 1.012 0 010-.639C3.423 7.51 7.36 4.5 12 4.5c4.638 0 8.573 3.007 9.963 7.178.07.207.07.431 0 .639C20.577 16.49 16.64 19.5 12 19.5c-4.638 0-8.573-3.007-9.963-7.178z"/>
                <path stroke-linecap="round" stroke-linejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/>
              </svg>
            </button>
            <a :href="`${apiUrl}/presentation_templates/${tpl.id}/download`" target="_blank" title="Download"
              class="tpl-action-btn" style="color: rgb(0,150,180);">
              <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                <path stroke-linecap="round" stroke-linejoin="round" d="M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75V16.5M16.5 12L12 16.5m0 0L7.5 12m4.5 4.5V3"/>
              </svg>
            </a>
          </div>
        </div>
      </div>
    </div>

    <!-- Template preview modal -->
    <Teleport to="body">
      <div v-if="templatePreview.open" class="fixed inset-0 z-50 flex items-center justify-center p-4"
        @click.self="closeTemplatePreview">
        <div class="absolute inset-0 bg-black/40 backdrop-blur-sm" @click="closeTemplatePreview"></div>
        <div class="relative w-full max-w-4xl bg-white rounded-2xl shadow-2xl overflow-hidden flex flex-col" style="height: 85vh;">
          <div class="flex items-center justify-between px-6 py-4 border-b border-gray-100 flex-shrink-0">
            <h2 class="font-semibold text-gray-800 text-base truncate pr-4">{{ templatePreview.name }}</h2>
            <div class="flex items-center gap-2 flex-shrink-0">
              <a v-if="templatePreview.id" :href="`${apiUrl}/presentation_templates/${templatePreview.id}/download`" target="_blank"
                class="px-3 py-1.5 text-xs rounded-full font-semibold text-white hover:opacity-90 transition"
                style="background-color: rgb(0,150,180);">
                Download
              </a>
              <button @click="closeTemplatePreview" class="p-1.5 rounded-lg text-gray-400 hover:text-gray-600 hover:bg-gray-100 transition">
                <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
                </svg>
              </button>
            </div>
          </div>
          <div class="flex-1 bg-gray-50">
            <iframe v-if="templatePreview.src" :src="templatePreview.src" class="w-full h-full" style="border:none;"></iframe>
          </div>
        </div>
      </div>
    </Teleport>

  </div>
</template>

<script>
import { fetchData } from "@/services/apiService";
import { useAuthStore } from "@/store/authStore";
import axios from "axios";

export default {
    name: 'MyAbstracts',
    data() {
        return {
            isLoading: true,
            abstracts: [],
            isPaidPresenter: false,
            apiUrl: import.meta.env.VITE_API_URL,
            templates: [],
            templatesLoading: false,
            templatePreview: { open: false, id: null, name: '', src: '' },
        };
    },
    mounted() {
        this.getMyAbstracts();
        this.checkPresenterStatus();
    },
    setup() {
        const authStore = useAuthStore();
        const user = authStore.loginUser;
        const token = authStore.accessToken;
        return { user, token };
    },
    methods: {
        async checkPresenterStatus() {
            try {
                const res = await axios.get(
                    `${this.apiUrl}/abstracts/my-presenter-status`,
                    { headers: { Authorization: `Bearer ${this.token}` } }
                );
                this.isPaidPresenter = res.data.is_paid_presenter === true;
                if (this.isPaidPresenter) this.loadTemplates();
            } catch (e) {
                console.warn("Could not check presenter status:", e);
                this.isPaidPresenter = false;
            }
        },

        async loadTemplates() {
            this.templatesLoading = true;
            try {
                const res = await axios.get(`${this.apiUrl}/presentation_templates`, {
                    headers: { Authorization: `Bearer ${this.token}` },
                });
                this.templates = res.data || [];
            } catch (e) {
                console.error("Could not load templates:", e);
            } finally {
                this.templatesLoading = false;
            }
        },

        isPreviewable(name) {
            const ext = (name || '').split('.').pop().toLowerCase();
            return ['pdf', 'ppt', 'pptx', 'doc', 'docx'].includes(ext);
        },

        openTemplatePreview(tpl) {
            const ext = (tpl.original_name || '').split('.').pop().toLowerCase();
            const fileUrl = `${this.apiUrl}/presentation_templates/${tpl.id}/preview`;
            const src = ext === 'pdf'
                ? fileUrl
                : `https://view.officeapps.live.com/op/embed.aspx?src=${encodeURIComponent(fileUrl)}`;
            this.templatePreview = { open: true, id: tpl.id, name: tpl.original_name, src };
        },

        closeTemplatePreview() {
            this.templatePreview = { open: false, id: null, name: '', src: '' };
        },

        fileIcon(name) {
            const ext = (name || '').split('.').pop().toLowerCase();
            return { pptx: '📊', ppt: '📊', docx: '📄', doc: '📄', pdf: '📕', zip: '🗜️' }[ext] || '📎';
        },

        async getMyAbstracts() {
            try {
                const response = await fetchData("abstracts/my-submissions", 1, 100, "");
                const data = response.data || response || [];
                this.abstracts = data.map(a => ({
                    ...a,
                    _expanded: false,
                    _file: null,
                    _uploading: false,
                    _uploadMsg: '',
                    _uploadErr: false,
                }));
            } catch (error) {
                console.error("Error fetching my abstracts:", error);
                this.abstracts = [];
            } finally {
                this.isLoading = false;
            }
        },

        async uploadPresentation(abstract) {
            if (!abstract._file) return;
            abstract._uploading = true;
            abstract._uploadMsg = '';
            abstract._uploadErr = false;
            try {
                const form = new FormData();
                form.append('file', abstract._file);
                await axios.post(
                    `${this.apiUrl}/abstracts/${abstract.id}/upload-presentation`,
                    form,
                    {
                        headers: {
                            Authorization: `Bearer ${this.token}`,
                            'Content-Type': 'multipart/form-data',
                        },
                    }
                );
                abstract._uploadMsg = 'Uploaded successfully!';
                abstract.presentation_file = 'uploaded'; // flag so badge shows
                abstract.presentation_uploaded_at = new Date().toISOString();
                abstract._file = null;
            } catch (e) {
                abstract._uploadMsg = e.response?.data?.detail || 'Upload failed.';
                abstract._uploadErr = true;
            } finally {
                abstract._uploading = false;
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

<style scoped>
.tpl-action-btn {
  @apply flex items-center justify-center w-8 h-8 rounded-lg border border-gray-200 bg-white hover:bg-gray-50 transition-colors flex-shrink-0;
}
</style>
