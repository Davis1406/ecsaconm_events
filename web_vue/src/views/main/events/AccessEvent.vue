<template>
  <div class="flex flex-col space-y-3 flex-1">
    <HeaderView :headerTitle="headerTitle" />
    <SpinnerComponent v-if="isLoading" />
    <div v-else class="rounded-2xl border border-mercury-500 p-3">
      <div class="flex flex-col space-y-1">
        <div class="text-3xl font-semibold font-roboto-thin text-bondi-blue-500">
          <span>{{ event.event }}</span>
        </div>
        <div class="flex text-sm items-center space-x-1">
          <div class="rounded-sm flex flex-1 py-1 space-x-1">
            <span>{{ event.description }}</span>
          </div>
        </div>
        <div class="flex text-sm items-center space-x-1">
          <div class="rounded-sm flex flex-1 py-1 space-x-1">
            <UserGroupIcon class="w-5 h-5 text-bondi-blue-500" />
            <span class="font-bold">:</span>
            <span>{{ event.organiser }}</span>
          </div>
        </div>
        <div class="flex text-md space-x-1">
          <div class="rounded-sm flex flex-1 py-1 space-x-1">
            <MapPinIcon class="w-5 h-5 text-bondi-blue-500" />
            <span class="font-bold">:</span>
            <span>{{ event.location }}</span>
          </div>
        </div>
        <div class="flex text-sm items-center space-x-1">
          <div class="rounded-sm flex flex-row flex-1 items-center py-1 space-x-1">
            <CalendarDaysIcon class="w-5 h-5 text-bondi-blue-500" />
            <span class="font-bold">:</span>
            <span>{{ formatDate(event.start_date) }} - {{ formatDate(event.end_date) }}</span>
          </div>
        </div>
      </div>
    </div>

    <div class="flex flex-row items-baseline text-2xl font-roboto-light font-semibold text-abbey-500">
      Event resources and links
    </div>
    <div class="flex space-x-2">
      <button @click="openResourceUploadModal" v-if="permissions.includes('ADD_EVENT')"
        class="mt-2 px-4 py-2 text-white-200 bg-daintree-600 hover:bg-daintree-400 rounded-md cursor-pointer">
        Add Resource</button>
      <button @click="openLinkModal" v-if="permissions.includes('ADD_EVENT')"
        class="mt-2 px-4 py-2 text-white-200 bg-daintree-600 hover:bg-daintree-400 rounded-md cursor-pointer">
        Add Link</button>
    </div>
    <div class="rounded-2xl border border-white-600 shadow-sm p-4 text-abbey-500 flex flex-col space-y-2">
      <!-- <span class="text-xl font-semibold font-roboto-thin text-bondi-blue-500">Files (Click the link to download
        file)</span> -->
      <div v-if="resources.length > 0">
        <span v-for="(resource) in resources" :key="resource.id">
          <a class="text-dodger-blue-600 hover:text-dodger-blue-400" :href="getFullImageUrl(resource.filepath)"
            :download="file_name">{{
              resource.file_name }}</a>
        </span>
      </div>
      <!-- <div v-else>
        <span class="italic">No files uploaded yet, check again later</span>
      </div> -->
      <!-- <span class="text-xl font-semibold font-roboto-thin text-bondi-blue-500">Links (Click on a link to access)</span> -->
      <ul v-if="links.length > 0" class="list-outside hover:list-inside list-decimal">
        <li class="flex flex.row" v-for="(link) in links" :key="link.id">
          <a class="text-dodger-blue-600 hover:text-dodger-blue-400" :href="link.link">{{ link.link_name }}</a>
        </li>
      </ul>
      <!-- <div v-else>
        <span class="italic">No links have been added yet, check again later</span>
      </div> -->
    </div>
    <event-resource-modal :show="showResourceModal" @close="closeResourceUploadModal" :event_id="event_id">
    </event-resource-modal>
    <event-link-modal :show="showLinkModal" @close="closeLinkModal" :event_id="event_id">
    </event-link-modal>
  </div>
</template>

<script>
import { fetchItem } from "@/services/apiService";
import { MapPinIcon, CalendarDaysIcon, UserGroupIcon } from '@heroicons/vue/24/solid';
import HeaderView from '@/includes/Header.vue';
import SpinnerComponent from "@/components/Spinner.vue";
import { useAuthStore } from "@/store/authStore";
import EventResourceModal from "@/components/EventResourceModal.vue";
import EventLinkModal from "@/components/EventLinkModal.vue";

export default {
  name: "EventView",
  components: {
    HeaderView, SpinnerComponent, MapPinIcon, CalendarDaysIcon, UserGroupIcon, EventResourceModal, EventLinkModal
  },
  data() {
    return {
      headerTitle: "Event details",
      id: this.$route.params.id,
      isLoading: true,
      event: {},
      resources: {},
      links: {},
      participants: [],
      appUrl: import.meta.env.VITE_API_URL,
      showParticipantModal: false,
      currentPage: 1,
      totalPages: "",
      pageSize: 20,
      apiUrl: import.meta.env.VITE_API_URL,
      searchPhrase: "",
      showResourceModal: false,
      showLinkModal: false
    };
  },
  mounted() {
    this.getEvent();
  },
  setup() {
    const authStore = useAuthStore();
    const raw = authStore.permissions || []
        const permissions = raw.map(p => typeof p === "string" ? p : p.permission_code);
    return { permissions };
  },
  methods: {
    async getEvent() {
      try {
        const response = await fetchItem("events", this.id, this.currentPage, this.pageSize, this.searchPhrase);
        this.event = response.event;
        this.participants = response.data;
        this.totalPages = response.pages;
        this.resources = response.resource_files;
        this.links = response.links;
        console.log(response);
        this.isLoading = false;
      } catch (error) {
        console.error("Error fetching event:", error);
        this.isLoading = false;
      }
    },
    formatDate(dateString) {
      const date = new Date(dateString);
      return date.toLocaleString("en-UK", {
        day: "2-digit",
        month: "2-digit",
        year: "numeric",
      });
    },
    openResourceUploadModal() {
      this.event_id = this.id
      this.showResourceModal = true
    },
    closeResourceUploadModal() {
      this.showResourceModal = false
    },
    openLinkModal() {
      this.event_id = this.id
      this.showLinkModal = true
    },
    closeLinkModal() {
      this.showLinkModal = false
    },
    getFullImageUrl(filePath) {
      return `${this.apiUrl}/${filePath}`;
    }
  },
};
</script>