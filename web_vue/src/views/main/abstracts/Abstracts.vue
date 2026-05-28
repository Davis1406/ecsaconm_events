<template>
    <div class="flex flex-col space-y-4 flex-1">
        <HeaderView :headerTitle="headerTitle"></HeaderView>
        <div class="flex flex-col space-y-4">
            <div class="flex sm:flex-row flex-col sm:justify-between sm:items-center items-start">
                <search-component @search="handleSearch"></search-component>
            </div>
            <SpinnerComponent v-if="isLoading" />
            <div v-else class="rounded-md border-2 border-white-600 shadow-sm text-abbey-500">
                <div class="">
                    <div class="flex bg-mercury-500 p-3 pt-2 pb-2 rounded-t-sm uppercase text-xs font-bold">
                        <div class="w-4/12 p-1">Title</div>
                        <div class="w-2/12 p-1">Event</div>
                        <div class="w-2/12 p-1">Submitter</div>
                        <div class="w-2/12 p-1">Status</div>
                        <div class="w-2/12 p-1">Date</div>
                    </div>
                    <div v-if="abstracts.length === 0" class="p-4 text-center text-sm text-abbey-500 italic">
                        No abstracts found.
                    </div>
                    <div
                        class="flex sm:flex-row flex-col p-3 pt-2 pb-2 text-sm items-center border-t-2 border-mercury-500 cursor-pointer hover:bg-ghost-300"
                        v-for="(abstract) in abstracts" :key="abstract.id"
                        @click="handleView(abstract.id)">
                        <div class="sm:w-4/12 w-full p-1 sm:font-light font-bold">{{ abstract.title }}</div>
                        <div class="sm:w-2/12 w-full p-1">{{ abstract.event }}</div>
                        <div class="sm:w-2/12 w-full p-1">{{ abstract.submitter_name }}</div>
                        <div class="sm:w-2/12 w-full p-1">
                            <span :class="statusBadgeClass(abstract.status)"
                                class="px-2 py-1 rounded-full text-xs font-semibold capitalize">
                                {{ abstract.status }}
                            </span>
                        </div>
                        <div class="sm:w-2/12 w-full p-1">{{ formatDate(abstract.created_at) }}</div>
                    </div>
                </div>
            </div>
            <div class="">
                <pagination-component :currentPage="currentPage" :totalPages="totalPages"
                    @page-change="handlePageChange">
                </pagination-component>
            </div>
        </div>
    </div>
</template>

<script>
import HeaderView from '@/includes/Header.vue'
import PaginationComponent from '@/components/PaginationComponent.vue'
import SearchComponent from '@/components/SearchComponent.vue'
import { fetchData } from "@/services/apiService";
import SpinnerComponent from "@/components/Spinner.vue";
import { useAuthStore } from "@/store/authStore";

export default {
    name: 'AbstractsView',
    components: {
        PaginationComponent, SearchComponent, HeaderView, SpinnerComponent
    },
    data() {
        return {
            headerTitle: "Abstracts",
            abstracts: [],
            isLoading: true,
            currentPage: 1,
            totalPages: "",
            pageSize: 20,
            searchPhrase: ""
        };
    },
    mounted() {
        this.getAbstracts();
    },
    setup() {
        const authStore = useAuthStore()
        const raw = authStore.permissions || []
        const permissions = raw.map(p => typeof p === "string" ? p : p.permission_code)
        return { permissions }
    },
    methods: {
        async getAbstracts() {
            try {
                const response = await fetchData("abstracts", (this.currentPage - 1) * this.pageSize, this.pageSize, this.searchPhrase);
                this.abstracts = response.data || response;
                this.totalPages = response.pages || 1;
                this.isLoading = false;
            } catch (error) {
                console.error("Error fetching abstracts:", error);
                this.isLoading = false;
            }
        },
        async handleSearch(searchQuery) {
            this.searchPhrase = searchQuery;
            this.currentPage = 1;
            this.getAbstracts();
        },
        async handlePageChange(newPage) {
            this.currentPage = newPage;
            this.getAbstracts();
        },
        handleView(id) {
            this.$router.push({ name: 'Abstract', params: { id: id } });
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
