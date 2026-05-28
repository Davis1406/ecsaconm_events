<template>
    <div class="flex flex-col space-y-4 flex-1">
        <HeaderView :headerTitle="headerTitle"></HeaderView>
        <div class="flex flex-col space-y-4">
            <div class="flex sm:flex-row flex-col sm:justify-between sm:items-center items-start">
                <search-component @search="handleSearch"></search-component>
                <router-link :to="{ name: 'AddParticipant' }" v-if="permissions.includes('ADD_PARTICIPANT')"
                    class="mt-2 px-4 py-2 text-white-200 bg-bondi-blue-500 hover:bg-bondi-blue-400 rounded-2xl">
                    Add Participant</router-link>
            </div>
            <SpinnerComponent v-if="isLoading" />
            <div v-else class="rounded-2xl border border-white-600 shadow-sm p-4 text-abbey-500">
                <div class="flex sm:flex-row flex-col bg-shuttle-gray-300 p-2 text-sm font-bold">
                    <div class="sm:w-4/12 w-full">Participant</div>
                    <div class="sm:w-2/12 w-full">Country</div>
                    <div class="sm:w-2/12 w-full">Paid Status</div>
                    <div class="sm:w-3/12 w-full">Email</div>
                    <div class="sm:w-2/12 w-full">Action</div>
                </div>
                <div class="flex sm:flex-row flex-col p-2 text-sm items-center"
                    v-for="(participant, index) in participants" :key="participant.id" :class="getRowClass(index)">
                    <div class="sm:w-4/12 w-full">{{ participant.title }}
                        <span class="uppercase">{{
                            participant.users.firstname }}</span> {{
                                participant.users.lastname }}
                    </div>
                    <div class="sm:w-2/12 w-full">{{ participant.country.country }}</div>
                    <div class="sm:w-2/12 w-full">{{ participant.users.phone }}</div>
                    <div class="sm:w-3/12 w-full">{{ participant.users.email }}</div>
                    <div class="flex space-x-2 sm:w-2/12 w-full">
                        <router-link v-if="permissions.includes('VIEW_PARTICIPANT')"
                            class="p-1 border border-st-tropaz-600 bg-st-tropaz-200 rounded-full"
                            :to="{ name: 'Participant', params: { id: participant.user_id } }">
                            <EyeIcon class="w-5 h-5 text-st-tropaz-600"></EyeIcon>
                        </router-link>
                        <router-link v-if="permissions.includes('UPDATE_PARTICIPANT')"
                            class="p-1 bg-mountain-meadow-300 border border-mountain-meadow-700 rounded-full"
                            :to="{ name: 'EditParticipant', params: { id: participant.user_id } }">
                            <PencilSquareIcon class=" w-5 h-5 text-mountain-meadow-900">
                            </PencilSquareIcon>
                        </router-link>
                        <div v-if="permissions.includes('DELETE_PARTICIPANT')"
                            class="p-1 border border-flamingo-600 bg-flamingo-400  rounded-full">
                            <TrashIcon class="w-5 h-5 text-flamingo-800"
                                @click="showDeleteConfirmation(participant.id)">
                            </TrashIcon>
                        </div>
                    </div>
                </div>
                <pagination-component :currentPage="currentPage" :totalPages="totalPages"
                    @page-change="handlePageChange">
                </pagination-component>
            </div>
        </div>
        <delete-confirmation-modal :show="showDeleteModal" @confirmed="deleteParticipant(deleteParticipantId)"
            @canceled="cancelDelete"></delete-confirmation-modal>
    </div>
</template>

<script>
import HeaderView from '@/includes/Header.vue'
import { EyeIcon, PencilSquareIcon, TrashIcon } from '@heroicons/vue/24/solid'
import PaginationComponent from '@/components/PaginationComponent.vue'
import SearchComponent from '@/components/SearchComponent.vue'
import { fetchData, deleteItem, updateItem } from "@/services/apiService";
import SpinnerComponent from "@/components/Spinner.vue";
import DeleteConfirmationModal from "@/components/DeleteConfirmationModal.vue";
import { useAuthStore } from "@/store/authStore";
import router from "@/router";

export default {
    name: 'ParticipantsView',
    components: {
        EyeIcon, PencilSquareIcon,
        TrashIcon, PaginationComponent,
        SearchComponent, HeaderView,
        SpinnerComponent, DeleteConfirmationModal
    },
    data() {
        return {
            headerTitle: "Participants",
            participants: {},
            isLoading: true,
            deleteParticipantId: null,
            showDeleteModal: false,
            currentPage: 1,
            totalPages: "",
            pageSize: 20,
            searchPhrase: ""
        };
    },
    mounted() {
        this.getParticipants();
    },
    setup() {
        const authStore = useAuthStore()
        const raw = authStore.permissions || []
        const permissions = raw.map(p => typeof p === 'string' ? p : p.permission_code)
        return { permissions }
    },
    methods: {
        async getParticipants() {
            this.isLoading = true
            try {
                const response = await fetchData("participants", (this.currentPage - 1) * this.pageSize, this.pageSize, this.searchPhrase);
                this.participants = response.data;
                this.totalPages = response.pages;
                this.isLoading = false;
            } catch (error) {
                console.error("Error fetching participants:", error);
                this.isLoading = false;
            }
        },
        async handleSearch(searchQuery) {
            this.searchPhrase = searchQuery
            this.getParticipants();
        },
        async handlePageChange(newPage) {
            this.currentPage = newPage;
            this.getParticipants();
        },
        async deleteParticipant(id) {
            this.isLoading = true;
            try {
                await deleteItem("participants", id);
                const index = this.participants.findIndex((participant) => participant.id === id);
                if (index !== -1) {
                    this.participants.splice(index, 1);
                }
                this.showDeleteModal = false;
                this.isLoading = false;
            } catch (error) {
                console.error("Error fetching participants:", error);
                this.isLoading = false;
                this.showDeleteModal = false;
            }
        },
        showDeleteConfirmation(id) {
            this.deleteParticipantId = id;
            this.showDeleteModal = true;
        },
        cancelDelete() {
            this.showDeleteModal = false;
        },
        getRowClass(index) {
            return index % 2 === 0 ? 'bg-st-tropaz-100' : 'bg-shuttle-gray-50';
        },
        async confirmPaid(id) {
            this.isLoading = true;
            try {
                const response = await updateItem(
                    "participants/paid",
                    id,
                );
                this.participant = response.data;
                this.isLoading = false;
                router.push("/participants");
            } catch (error) {
                console.error("Error fetching participants:", error);
                this.isLoading = false;
            }

        }
    }
}
</script>