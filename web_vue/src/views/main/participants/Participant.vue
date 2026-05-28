<template>
  <div class="flex flex-col space-y-4 flex-1">
    <HeaderView :headerTitle="headerTitle"></HeaderView>
    <div class="flex sm:flex-row flex-col sm:space-x-4 space-x-0 sm:space-y-0 space-y-4">
      <div class="sm:w-4/12 w-full space-y-1 rounded-2xl border border-white-600 shadow-sm p-4 text-abbey-500">
        <div class="px-3 p-2 rounded-xl text-white-50 text font-roboto-thin bg-daintree-600">Participant Profile
        </div>
        <div class="flex items-center justify-center py-4"><img src="@/assets/images/profile.png"
            class="rounded-xl border-4 border-st-tropaz-300 h-48"></div>
        <div class="flex flex-row p-3 py-1 rounded-md text-sm bg-st-tropaz-100">
          <div class="w-3/12 text-st-tropaz-900 font-bold">Name</div>
          <div class="flex-1">:
            {{ participant.title }}
            <span class="uppercase">{{ participant.firstname }}</span>
            {{
              participant.lastname
            }}
          </div>
        </div>
        <div class="flex flex-row p-3 py-1 rounded-md text-sm bg-st-tropaz-100">
          <div class="w-3/12 text-st-tropaz-900 font-bold">Phone</div>
          <div class="flex-1">: {{ participant.phone }}</div>
        </div>
        <div class="flex flex-row p-3 py-1 rounded-md text-sm bg-st-tropaz-100">
          <div class="w-3/12 text-st-tropaz-900 font-bold">Email</div>
          <div class="flex-1">: {{ participant.email }}</div>
        </div>
        <div class="flex flex-row p-3 py-1 rounded-md text-sm bg-st-tropaz-100">
          <div class="w-3/12 text-st-tropaz-900 font-bold">Institution</div>
          <div class="flex-1">:
            {{ participant.institution }}
          </div>
        </div>
        <div class="flex flex-row p-3 py-1 rounded-md text-sm bg-st-tropaz-100">
          <div class="w-3/12 text-st-tropaz-900 font-bold">Country</div>
          <div class="flex-1">:
            {{ participant.country }}
          </div>
        </div>
        <div class="flex flex-row py-1 rounded-md text-sm">
          <router-link v-if="permissions.includes('UPDATE_PARTICIPANT')"
            :to="{ name: 'EditParticipant', params: { id: participant_id } }"
            class="mt-2 px-4 py-2 text-white-100 bg-bondi-blue hover:bg-bondi-blue-400 rounded-xl">Update
            Profile</router-link>
        </div>
      </div>
      <div class="flex-1 space-y-2 rounded-2xl border border-white-600 shadow-sm p-4 text-abbey-500">
        <div class="px-3 p-2 rounded-xl text-white-50 text font-roboto-thin te bg-daintree-600">Participant Event List
        </div>

        <div v-if="events > 0">
          <SpinnerComponent v-if="isLoading" />
          <div v-else
            class="flex flex-row px-3 py-1 items-center space-x-4 border-2 border-shuttle-gray-200 rounded-xl text-sm"
            v-for="(event, index) in events" :key="event.id" :class="getRowClass(index)">
            {{ events }}
            <div class="flex-1">{{ event.event }}</div>
            <div class="text-flamingo font-semibold"> {{
              formatDate(event.updated_date) }}</div>
            <div class="flex">
              <CheckBadgeIcon class="text-mountain-meadow-900 w-8 h-8"></CheckBadgeIcon>
              <XCircleIcon class="text-flamingo w-8 h-8"></XCircleIcon>
            </div>
          </div>
        </div>
        <div class="p-4 block text-center italic text-flamingo-700">--Participant has not events--</div>

      </div>
    </div>
  </div>
</template>
<script>
import { fetchItem } from "@/services/apiService";
import HeaderView from '@/includes/Header.vue'
import SpinnerComponent from "@/components/Spinner.vue";
import { useAuthStore } from "@/store/authStore";

export default {
  name: "ParticipantView",
  components: {
    HeaderView, SpinnerComponent
  },
  data() {
    return {
      headerTitle: "Participant details",
      id: this.$route.params.id,
      isLoading: true,
      participant: {},
      events: {},
      currentPage: 1,
      totalPages: "",
      pageSize: 20,
      searchPhrase: ""
    };
  },
  mounted() {
    this.getParticipant();
  },
  setup() {
    const authStore = useAuthStore()
    const raw = authStore.permissions || []
    const permissions = raw.map(p => typeof p === "string" ? p : p.permission_code)
    return { permissions }
  },
  methods: {
    async getParticipant() {
      try {
        const response = await fetchItem("participants", this.id);
        this.participant = response.participant;
        this.events = response.events;
        this.isLoading = false;
      } catch (error) {
        console.error("Error fetching participants:", error);
        this.isLoading = false;
      }
    },
    getRowClass(index) {
      return index % 2 === 0 ? 'bg-athens-gray-400' : 'bg-athens-gray-100';
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
  },
};
</script>
