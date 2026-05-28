<template>
    <div class="flex flex-col space-y-4 flex-1">
        <HeaderView :headerTitle="headerTitle"></HeaderView>
        <div class="flex flex-col space-y-4">
            <div class="flex sm:flex-row flex-col sm:justify-between sm:items-center items-start">
                <search-component @search="handleSearch"></search-component>
                <router-link :to="{ name: 'AddEvent' }" v-if="permissions.includes('ADD_EVENT')"
                    class="mt-2 px-4 py-2 text-white font-semibold rounded-md transition hover:opacity-90"
                    style="background-color: rgb(254,80,103);">
                    Add Event</router-link>
            </div>
            <SpinnerComponent v-if="isLoading" />
            <div v-else class="rounded-md border-2 border-white-600 shadow-sm text-abbey-500">
                <div class="">
                    <div class="flex bg-mercury-500 p-3 pt-2 pb-2 rounded-t-sm uppercase text-xs font-bold">
                        <div class="w-6/12 p-1">Event Title</div>
                        <div class="w-2/12 p-1">Date</div>
                        <div class="w-2/12 p-1">Status</div>
                        <div class="w-2/12 p-1 text-end">Action</div>
                    </div>
                    <div class="flex sm:flex-row flex-col p-3 pt-2 pb-2 text-sm items-center border-t-2 border-mercury-500"
                        v-for="(event) in events" :key="event.id">
                        <div class="sm:w-6/12 w-full p-1 sm:font-light font-bold">{{ event.event }}</div>
                        <div class="sm:w-2/12 w-full p-1">{{ formatDate(event.start_date) }}</div>
                        <div class="sm:w-2/12 w-full p-1">{{ formartStatus(event.start_date) }}</div>
                        <div class="flex sm:w-2/12 w-full p-1 sm:justify-end justify-start">
                            <DropdownComponent @view="handleView(event.id)" @edit="handleEdit(event.id)"
                                @delete="handleDelete(event.id)" />
                        </div>
                    </div>
                </div>
            </div>
            <div class="">
                <pagination-component :currentPage="currentPage" :totalPages="totalPages"
                    @page-change="handlePageChange">
                </pagination-component>
            </div>
        </div>
        <delete-confirmation-modal :show="showDeleteModal" @confirmed="deleteEvent(deleteEventId)"
            @canceled="cancelDelete"></delete-confirmation-modal>
    </div>
</template>

<script>
import HeaderView from '@/includes/Header.vue'
import PaginationComponent from '@/components/PaginationComponent.vue'
import SearchComponent from '@/components/SearchComponent.vue'
import { fetchData, deleteItem } from "@/services/apiService";
import SpinnerComponent from "@/components/Spinner.vue";
import DeleteConfirmationModal from "@/components/DeleteConfirmationModal.vue";
import DropdownComponent from "@/components/ActionComponent.vue";
import { useAuthStore } from "@/store/authStore";

export default {
    name: 'EventsView',
    components: {
        PaginationComponent, SearchComponent, HeaderView, SpinnerComponent, DeleteConfirmationModal, DropdownComponent
    },
    data() {
        return {
            headerTitle: "Events",
            events: {},
            isLoading: true,
            showDeleteModal: false,
            deleteEventId: null,
            currentPage: 1,
            totalPages: "",
            pageSize: 20,
            searchPhrase: ""
        };
    },
    mounted() {
        this.getEvents();
    },
    setup() {
        const authStore = useAuthStore()
        const raw = authStore.permissions || []
        const permissions = raw.map(p => typeof p === "string" ? p : p.permission_code)
        return { permissions }
    },
    methods: {
        async getEvents() {
            try {
                const response = await fetchData("events", (this.currentPage - 1) * this.pageSize, this.pageSize, this.searchPhrase);
                this.events = response.data;
                this.totalPages = response.pages;
                this.isLoading = false;
            } catch (error) {
                console.error("Error fetching events:", error);
                this.isLoading = false;
            }
        },
        async handleSearch(searchQuery) {
            this.searchPhrase = searchQuery
            this.getEvents();
        },
        async handlePageChange(newPage) {
            this.currentPage = newPage;
            this.getEvents();
        },
        async deleteEvent(id) {
            this.isLoading = true;
            try {
                await deleteItem("events", id);
                const index = this.events.findIndex((event) => event.id === id);
                if (index !== -1) {
                    this.events.splice(index, 1);
                }
                this.showDeleteModal = false;
                this.isLoading = false;
            } catch (error) {
                console.error("Error fetching events:", error);
                this.isLoading = false;
                this.showDeleteModal = false;
            }
        },
        showDeleteConfirmation(id) {
            this.deleteEventId = id;
            this.showDeleteModal = true;
        },
        cancelDelete() {
            this.showDeleteModal = false;
        },
        getRowClass(index) {
            return index % 2 === 0 ? 'bg-st-tropaz-100' : 'bg-shuttle-gray-50';
        },

        handleView(id) {
            this.$router.push({ name: 'Event', params: { id: id } });
        },
        handleEdit(id) {
            this.$router.push({ name: 'EditEvent', params: { id: id } });
        },
        handleDelete(id) {
            this.deleteEventId = id;
            this.showDeleteModal = true;
        },
        formatDate(dateString) {
            const date = new Date(dateString);
            const formattedDate = date.toLocaleString("en-UK", {
                day: "2-digit",
                month: "2-digit",
                year: "numeric",
            });
            return formattedDate;
        },
        formartStatus(dateString) {
            const renewalDate = new Date(dateString);
            const today = new Date();
            if (renewalDate.getTime() > today.getTime()) {
                return "Active";
            } else {
                return "Expired";
            }
        },
    }
}
</script>