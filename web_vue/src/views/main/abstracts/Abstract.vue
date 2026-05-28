<template>
    <SpinnerComponent v-if="isLoading" />
    <div v-else class="flex flex-col space-y-4 flex-1">
        <HeaderView :headerTitle="headerTitle" />

        <div class="flex items-center space-x-2">
            <button @click="$router.push({ name: 'Abstracts' })"
                class="px-4 py-2 text-sm bg-mercury-500 hover:bg-mercury-600 text-abbey-500 rounded-md">
                &larr; Back to Abstracts
            </button>
        </div>

        <div class="p-3 px-4 rounded-2xl text-sm bg-green-100 border border-green-400 text-green-800"
            v-if="successMsg">{{ successMsg }}</div>
        <div class="p-3 px-4 rounded-2xl text-sm bg-red-100 border border-red-400 text-red-800"
            v-if="errorMsg">{{ errorMsg }}</div>

        <div class="rounded-md border-2 border-white-600 shadow-sm text-abbey-500 p-6 space-y-4">
            <div class="flex sm:flex-row flex-col sm:justify-between sm:items-start items-start space-y-2 sm:space-y-0">
                <div class="flex-1">
                    <h2 class="text-2xl font-semibold text-bondi-blue-500">{{ abstract.title }}</h2>
                    <div class="text-sm text-abbey-500 mt-1">
                        Submitted: {{ formatDate(abstract.created_at) }}
                    </div>
                </div>
                <span :class="statusBadgeClass(abstract.status)"
                    class="px-3 py-1 rounded-full text-sm font-semibold capitalize ml-4">
                    {{ abstract.status }}
                </span>
            </div>

            <div class="grid sm:grid-cols-2 gap-4 text-sm">
                <div>
                    <span class="font-bold text-abbey-500">Event:</span>
                    <span class="ml-2">{{ abstract.event }}</span>
                </div>
                <div>
                    <span class="font-bold text-abbey-500">Submitter:</span>
                    <span class="ml-2">{{ abstract.submitter_name }}</span>
                </div>
                <div>
                    <span class="font-bold text-abbey-500">Institution / Affiliation:</span>
                    <span class="ml-2">{{ abstract.institution || abstract.affiliation || '—' }}</span>
                </div>
                <div v-if="abstract.authors">
                    <span class="font-bold text-abbey-500">Authors:</span>
                    <span class="ml-2">{{ formatAuthors(abstract.authors) }}</span>
                </div>
            </div>

            <div class="border-t border-mercury-500 pt-4">
                <h3 class="font-bold text-abbey-500 mb-2">Abstract Body</h3>
                <p class="text-sm leading-relaxed whitespace-pre-wrap">{{ abstract.abstract_text || abstract.body || abstract.content }}</p>
            </div>

            <div v-if="abstract.keywords" class="text-sm">
                <span class="font-bold text-abbey-500">Keywords:</span>
                <span class="ml-2 italic">{{ abstract.keywords }}</span>
            </div>
        </div>

        <div class="rounded-md border-2 border-white-600 shadow-sm p-6">
            <h3 class="font-bold text-abbey-500 mb-4">Update Status</h3>
            <div class="flex sm:flex-row flex-col space-y-2 sm:space-y-0 sm:space-x-3 items-start sm:items-center">
                <button @click="updateStatus('approved')"
                    :disabled="isUpdating"
                    class="px-4 py-2 rounded-md text-white bg-green-600 hover:bg-green-500 disabled:opacity-50 text-sm">
                    Approve
                </button>
                <button @click="updateStatus('rejected')"
                    :disabled="isUpdating"
                    class="px-4 py-2 rounded-md text-white bg-red-600 hover:bg-red-500 disabled:opacity-50 text-sm">
                    Reject
                </button>
                <button @click="updateStatus('under_review')"
                    :disabled="isUpdating"
                    class="px-4 py-2 rounded-md text-white bg-bondi-blue-500 hover:bg-bondi-blue-400 disabled:opacity-50 text-sm">
                    Mark Under Review
                </button>
            </div>
        </div>
    </div>
</template>

<script>
import { fetchItem, updateItem } from "@/services/apiService";
import HeaderView from '@/includes/Header.vue';
import SpinnerComponent from "@/components/Spinner.vue";
import { useAuthStore } from "@/store/authStore";

export default {
    name: 'AbstractView',
    components: {
        HeaderView, SpinnerComponent
    },
    data() {
        return {
            headerTitle: "Abstract Detail",
            id: this.$route.params.id,
            isLoading: true,
            isUpdating: false,
            abstract: {},
            successMsg: "",
            errorMsg: "",
        };
    },
    mounted() {
        this.getAbstract();
    },
    setup() {
        const authStore = useAuthStore();
        const raw = authStore.permissions || []
        const permissions = raw.map(p => typeof p === "string" ? p : p.permission_code);
        return { permissions };
    },
    methods: {
        async getAbstract() {
            try {
                const response = await fetchItem("abstracts", this.id);
                this.abstract = response.data || response;
                this.isLoading = false;
            } catch (error) {
                console.error("Error fetching abstract:", error);
                this.isLoading = false;
            }
        },
        async updateStatus(status) {
            this.isUpdating = true;
            this.successMsg = "";
            this.errorMsg = "";
            try {
                await updateItem("abstracts", this.id, { status });
                this.abstract.status = status;
                this.successMsg = `Abstract status updated to "${status}" successfully.`;
            } catch (error) {
                console.error("Error updating abstract:", error);
                this.errorMsg = error.response?.data?.detail || "Failed to update abstract status.";
            } finally {
                this.isUpdating = false;
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
        formatAuthors(authors) {
            if (Array.isArray(authors)) {
                return authors.map(a => `${a.firstname || ''} ${a.lastname || ''}`.trim()).join(', ');
            }
            return authors || '—';
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
};
</script>
