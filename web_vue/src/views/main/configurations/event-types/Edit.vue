<template>
  <div class="flex flex-col space-y-4 flex-1">
    <HeaderView :headerTitle="headerTitle"></HeaderView>
    <SpinnerComponent v-if="isLoading" />
    <div v-else class="rounded-2xl bg-catskill-white-100 shadow-sm p-4">
      <form class="flex flex-col sm:w-5/12 w-full space-y-4" @submit.prevent="editEventType" method="POST">
        <label class="block">
          <span class="after:content-['*'] after:ml-0.5 after:text-red-500 block text-sm font-medium text-slate-700">
            Event Type
          </span>
          <input type="input" name="event_type" v-model="eventTypeData.event_type"
            class="mt-2 px-3 py-3 bg-white border border-1 shadow-sm border-mid-gray-300 placeholder-slate-400 focus:outline-none focus:border-sky-500 focus:ring-sky-500 block w-full rounded-xl sm:text-sm focus:ring-1"
            placeholder="Event type" />
        </label>
        <label class="block">
          <span class="after:content-['*'] after:ml-0.5 after:text-red-500 block text-sm font-medium text-slate-700">
            Description
          </span>
          <textarea name="description" v-model="eventTypeData.description"
            class="mt-2 px-3 py-3 bg-white border border-1 shadow-sm border-mid-gray-300 placeholder-slate-400 focus:outline-none focus:border-sky-500 focus:ring-sky-500 block w-full rounded-xl sm:text-sm focus:ring-1"
            placeholder="Description" required></textarea>
        </label>
        <div class="flex flex-row space-x-4">
          <button type="submit" class="mt-2 px-4 py-2 text-white-100 bg-bondi-blue hover:bg-bondi-blue-400 rounded-2xl">
            Edit event type
          </button>
          <router-link :to="{ name: 'EventTypes' }"
            class="mt-2 px-4 py-2 boder border-2 border-abbey-400 hover:border-abbey-200 rounded-2xl">Cancel</router-link>
        </div>
      </form>
    </div>
  </div>
</template>
<script>
import { updateItem, fetchItem } from "@/services/apiService";
import HeaderView from '@/includes/Header.vue'
import SpinnerComponent from "@/components/Spinner.vue";
import router from "@/router";

export default {
  name: "EditEventTypeView",
  components: {
    HeaderView, SpinnerComponent
  },
  data() {
    return {
      headerTitle: "Edit event type",
      id: this.$route.params.id,
      eventTypeData: {
        event_type: "",
        description: "",
      },
      isLoading: false,
      event_type: {},
    };
  },
  mounted() {
    this.getEventType();
  },
  methods: {
    async editEventType() {
      this.isLoading = true;
      try {
        const response = await updateItem(
          "event_types",
          this.id,
          this.eventTypeData
        );
        this.event_type = response.data;
        this.isLoading = false;
        router.push("/event-types");
      } catch (error) {
        console.error("Error editing event type:", error);
        this.isLoading = false;
      }
    },
    async getEventType() {
      try {
        const response = await fetchItem("event_types", this.id);
        this.eventTypeData.event_type = response.event_type.event_type;
        this.eventTypeData.description = response.event_type.description;
        this.isLoading = false;
      } catch (error) {
        console.error("Error fetching event type:", error);
        this.isLoading = false;
      }
    },
  },
};
</script>
