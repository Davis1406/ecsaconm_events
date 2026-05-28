<template>
    <div class="flex flex-col space-y-4 flex-1">
        <HeaderView :headerTitle="headerTitle"></HeaderView>
        <div class="flex flex-col space-y-4">
            <div class="flex sm:flex-row flex-col sm:justify-between sm:items-center items-start">
                <search-component @search="handleSearch"></search-component>
                <router-link :to="{ name: 'AddEventType' }" v-if="permissions.includes('ADD_EVENT_TYPE')"
                    class="mt-2 px-4 py-2 text-white-200 bg-bondi-blue-500 hover:bg-bondi-blue-400 rounded-2xl">
                    Add Event type</router-link>
            </div>
            <SpinnerComponent v-if="isLoading" />
            <div v-else class="rounded-2xl border border-white-600 shadow-sm p-4 text-abbey-500">
                <div class="flex sm:flex-row flex-col bg-shuttle-gray-300 p-2 text-sm font-bold">
                    <div class="sm:w-4/12 w-full">Event type</div>
                    <div class="sm:w-7/12 w-full">Description</div>
                    <div class="sm:w-1/12 w-full">Action</div>
                </div>
                <div class="flex sm:flex-row flex-col p-2 text-sm items-center"
                    v-for="(event_type, index) in event_types" :key="event_type.id" :class="getRowClass(index)">
                    <div class="sm:w-4/12 w-full">{{ event_type.event_type }}</div>
                    <div class="sm:w-7/12 w-full">{{ event_type.description }}</div>
                    <div class="flex space-x-2 sm:w-1/12 w-full">
                        <router-link v-if="permissions.includes('UPDATE_EVENT_TYPE')" title="Edit"
                            class="p-1 bg-mountain-meadow-300 border border-mountain-meadow-700 rounded-full"
                            :to="{ name: 'EditEventType', params: { id: event_type.id } }">
                            <PencilSquareIcon class=" w-5 h-5 text-mountain-meadow-900">
                            </PencilSquareIcon>
                        </router-link>
                        <div v-if="permissions.includes('DELETE_EVENT_TYPE')" title="Delete"
                            class="p-1 border border-flamingo-600 bg-flamingo-400 rounded-full cursor-pointer">
                            <TrashIcon class="w-5 h-5 text-flamingo-800" @click="showDeleteConfirmation(event_type.id)">
                            </TrashIcon>
                        </div>
                    </div>
                </div>
                <pagination-component :currentPage="currentPage" :totalPages="totalPages"
                    @page-change="handlePageChange">
                </pagination-component>
            </div>
        </div>
        <delete-confirmation-modal :show="showDeleteModal" @confirmed="deleteEventType(deleteEventTypeId)"
            @canceled="cancelDelete"></delete-confirmation-modal>
    </div>
</template>

<script>
import HeaderView from '@/includes/Header.vue'
import { PencilSquareIcon, TrashIcon } from '@heroicons/vue/24/solid'
import PaginationComponent from '@/components/PaginationComponent.vue'
import SearchComponent from '@/components/SearchComponent.vue'

import { fetchData, deleteItem } from "@/services/apiService";
import SpinnerComponent from "@/components/Spinner.vue";
import DeleteConfirmationModal from "@/components/DeleteConfirmationModal.vue";
import { useAuthStore } from "@/store/authStore";

export default {
    name: 'EventTypesView',
    components: {
        PencilSquareIcon, TrashIcon, PaginationComponent, SearchComponent, HeaderView, SpinnerComponent, DeleteConfirmationModal
    },
    data() {
        return {
            headerTitle: "Event Type",
            event_types: {},
            isLoading: true,
            showDeleteModal: false,
            deletePersonnelId: null,
            currentPage: 1,
            totalPages: "",
            pageSize: 20,
            searchPhrase: ""
        };
    },
    mounted() {
        this.getEventTypes();
    },
    setup() {
        const authStore = useAuthStore()
        const raw = authStore.permissions || []
        const permissions = raw.map(p => typeof p === "string" ? p : p.permission_code)
        return { permissions }
    },
    methods: {
        async getEventTypes() {
            try {
                const response = await fetchData("event_types", (this.currentPage - 1) * this.pageSize, this.pageSize, this.searchPhrase);
                this.event_types = response.data;
                this.totalPages = response.pages;
                this.isLoading = false;
            } catch (error) {
                console.error("Error fetching event types:", error);
                this.isLoading = false;
            }
        },
        async handleSearch(searchQuery) {
            this.searchPhrase = searchQuery
            this.getEventTypes();
        },
        async handlePageChange(newPage) {
            this.currentPage = newPage;
            this.getEventTypes();
        },
        async deleteEventType(id) {
            this.isLoading = true;
            try {
                await deleteItem("event_types", id);
                const index = this.event_types.findIndex((event_type) => event_type.id === id);
                if (index !== -1) {
                    this.event_types.splice(index, 1);
                }
                this.showDeleteModal = false;
                this.isLoading = false;
            } catch (error) {
                console.error("Error fetching event types:", error);
                this.isLoading = false;
                this.showDeleteModal = false;
            }
        },
        showDeleteConfirmation(id) {
            this.deleteEventTypeId = id;
            this.showDeleteModal = true;
        },
        cancelDelete() {
            this.showDeleteModal = false;
        },
        getRowClass(index) {
            return index % 2 === 0 ? 'bg-st-tropaz-100' : 'bg-shuttle-gray-100';
        },
    }
}
</script>